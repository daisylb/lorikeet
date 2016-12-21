from django.db import models
from django.conf import settings
from decimal import Decimal
from model_utils.managers import InheritanceManager


class Cart(models.Model):
    """An in-progress shopping cart.

    These can be attached to a user, or they can have a null user and be
    referenced from a session.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    delivery_address = models.ForeignKey('cart.DeliveryAddress', blank=True, null=True)

    def get_grand_total(self):
        return sum(x.get_total() for x in self.items.select_subclasses().all())

    @property
    def delivery_address_subclass(self):
        if self.delivery_address_id is not None:
            return DeliveryAddress.objects.get_subclass(
                id=self.delivery_address_id)




class Order(models.Model):
    """A completed, paid order.
    """
    custom_invoice_id = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    guest_email = models.EmailField(blank=True)
    payment = models.ForeignKey('cart.Payment')
    delivery_address = models.ForeignKey('cart.DeliveryAddress')

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


class PaymentMethod(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)

    def make_payment(self, amount, description):
        raise NotImplemented("Provide a make_payment method in your "
                             "PaymentMethod subclass {}.".format(
                                 self.__class__.__name__))

    def assign_to_user(self, user):
        self.user = user


class Payment(models.Model):
    method = models.ForeignKey(PaymentMethod)


class DeliveryAddress(models.Model):
    """An address that an order can be shipped to.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,
                             related_name='delivery_addresses')

    objects = InheritanceManager()


class LineItem(models.Model):
    """An individual item that is either in a shopping cart or on an order.

    Subclasses of LineItem should provide a get_total method that should
    depend only on data stored on this model.
    """
    cart = models.ForeignKey(Cart, related_name='items', blank=True, null=True)
    order = models.ForeignKey(Order, related_name='items', blank=True, null=True)

    objects = InheritanceManager()

    class Meta:
        # Because IDs auto increment, ordering by ID has the same effect as
        # ordering by date added, but we don't have to store the date
        ordering = ('id',)

    def get_total(self):
        raise NotImplemented("Provide a get_total method in your LineItem "
                             "subclass {}.".format(self.__class__.__name__))

    def save(self, *args, **kwargs):
        if self.order is not None and not getattr(self, '_new_order'):
            raise ValueError("Cannot modify a cart item attached to an order.")
        return super().save(*args, **kwargs)
