from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.module_loading import import_string
from model_utils.managers import InheritanceManager

from . import settings as lorikeet_settings
from . import exceptions


class Cart(models.Model):
    """An in-progress shopping cart.

    Carts are associated with the user for an authenticated request, or with
    the session otherwise; in either case it can be accessed on
    ``request.cart``.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    delivery_address = models.ForeignKey(
        'lorikeet.DeliveryAddress', blank=True, null=True)
    payment_method = models.ForeignKey(
        'lorikeet.PaymentMethod', blank=True, null=True)

    def get_grand_total(self):
        """Calculate the grand total for this cart."""
        return sum(x.get_total() for x in self.items.select_subclasses().all())

    @property
    def delivery_address_subclass(self):
        """Get the delivery address instance selected for this cart.

        Returns an instance of one of the registered
        :class:`~lorikeet.models.DeliveryAddress` subclasses.
        """
        if self.delivery_address_id is not None:
            return DeliveryAddress.objects.get_subclass(
                id=self.delivery_address_id)

    @property
    def payment_method_subclass(self):
        """Get the payment method instance selected for this cart.

        Returns an instance of one of the registered
        :class:`~lorikeet.models.PaymentMethod` subclasses.
        """
        if self.payment_method_id is not None:
            return PaymentMethod.objects.get_subclass(
                id=self.payment_method_id)

    def is_complete(self, raise_exc=False):
        """Determine if this cart is able to be checked out.

        If this function returns ``False``, the ``.errors`` attribute will
        be set to a :class:`~lorikeet.exceptions.IncompleteCartErrorSet`
        containing all of the reasons the cart cannot be checked out.

        :param raise_exc: If ``True`` and there are errors, raise the
            resulting :class:`~lorikeet.exceptions.IncompleteCartErrorSet`
            instead of just returning ``False``.
        :type raise_exc: bool
        :return: Whether this cart can be checked out.
        :rtype: bool
        """

        # Use the .errors attribute to effectively memoize this function
        if not hasattr(self, 'errors'):
            self.errors = exceptions.IncompleteCartErrorSet()

            for checker in lorikeet_settings.LORIKEET_CART_COMPLETE_CHECKERS:
                checker_func = import_string(checker)
                try:
                    checker_func(self)
                except exceptions.IncompleteCartError as e:
                    self.errors.add(e)

        if raise_exc and self.errors:
            raise self.errors

        return not bool(self.errors)


class Order(models.Model):
    """A completed, paid order.
    """
    custom_invoice_id = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    guest_email = models.EmailField(blank=True)
    payment = models.ForeignKey('lorikeet.Payment', blank=True, null=True)
    delivery_address = models.ForeignKey(
        'lorikeet.DeliveryAddress', blank=True, null=True)

    @property
    def email(self):
        return self.user.email if self.user is not None else self.guest_email

    @property
    def invoice_id(self):
        """The ID of the invoice.

        If custom_invoice_id is set, it will be returned. Otherwise, the PK
        of the order object will be returned.
        """
        return self.custom_invoice_id or self.id

    @property
    def delivery_address_subclass(self):
        """Get the delivery address instance selected for this cart.

        Returns an instance of one of the registered
        :class:`~lorikeet.models.DeliveryAddress` subclasses.
        """
        if self.delivery_address_id is not None:
            return DeliveryAddress.objects.get_subclass(
                id=self.delivery_address_id)

    @property
    def payment_method_subclass(self):
        """Get the delivery address instance selected for this cart.

        Returns an instance of one of the registered
        :class:`~lorikeet.models.DeliveryAddress` subclasses.
        """
        return PaymentMethod.objects.get_subclass(
            id=self.payment.method_id)

    @property
    def payment_subclass(self):
        """Get the payment method instance selected for this cart.

        Returns an instance of one of the registered
        :class:`~lorikeet.models.PaymentMethod` subclasses.
        """
        return Payment.objects.get_subclass(
            id=self.payment_id)

    def get_absolute_url(self):
        """Get the absolute URL of an order details view.

        See the documentation for the ``LORIKEET_ORDER_DETAIL_VIEW``
        setting.
        """
        if lorikeet_settings.LORIKEET_ORDER_DETAIL_VIEW:
            return reverse(lorikeet_settings.LORIKEET_ORDER_DETAIL_VIEW,
                           kwargs={'id': self.id})


class PaymentMethod(models.Model):
    """A payment method, like a credit card or bank details.

    This model doesn't do anything by itself; you'll need to subclass it as
    described in the :doc:`Getting Started Guide <backend>`.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    active = models.BooleanField(default=True)

    objects = InheritanceManager()

    def make_payment(self, amount):
        raise NotImplementedError("Provide a make_payment method in your "
                                  "PaymentMethod subclass {}.".format(
                                      self.__class__.__name__))

    def assign_to_user(self, user):
        self.user = user


class Payment(models.Model):
    method = models.ForeignKey(PaymentMethod)


class DeliveryAddress(models.Model):
    """An address that an order can be delivered to.

    This model doesn't do anything by itself; you'll need to subclass it as
    described in the :doc:`Getting Started Guide <backend>`.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,
                             related_name='delivery_addresses')
    active = models.BooleanField(default=True)

    objects = InheritanceManager()


class LineItem(models.Model):
    """An individual item that is either in a shopping cart or on an order.

    This model doesn't do anything by itself; you'll need to subclass it as
    described in the :doc:`Getting Started Guide <backend>`.
    """
    cart = models.ForeignKey(Cart, related_name='items', blank=True, null=True)
    order = models.ForeignKey(
        Order, related_name='items', blank=True, null=True)

    objects = InheritanceManager()

    class Meta:
        # Because IDs auto increment, ordering by ID has the same effect as
        # ordering by date added, but we don't have to store the date
        ordering = ('id',)

    def get_total(self):
        """Returns the total amount to charge on this LineItem.

        By default this raises ``NotImplemented``; subclasses of this class
        need to override this.
        """
        raise NotImplemented("Provide a get_total method in your LineItem "
                             "subclass {}.".format(self.__class__.__name__))

    def save(self, *args, **kwargs):
        if self.order is not None and not getattr(self, '_new_order'):
            raise ValueError("Cannot modify a cart item attached to an order.")
        return super().save(*args, **kwargs)
