from . import models


class OrderMixin:
    """A mixin for views displaying orders.

    This mixin provides a ``get_queryset`` implementation that lists all
    orders belonging to the currently logged in user.
    """

    model = models.Order

    def get_queryset(self):
        return models.Order.objects.filter(user=self.request.user)
