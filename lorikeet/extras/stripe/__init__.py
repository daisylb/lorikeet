from django.apps import AppConfig
from django.conf import settings
import stripe


class StripeAppConfig(AppConfig):
    name = 'lorikeet.extras.stripe'
    verbose_name = "Lorikeet Stripe"

    def ready(self):
        stripe.api_key = settings.STRIPE_API_KEY

        from . import models, api_serializers
        from lorikeet.api_serializers import registry
        registry.register(models.StripeCard,
                          api_serializers.StripeCardSerializer)

default_app_config = 'lorikeet.extras.stripe.StripeAppConfig'
