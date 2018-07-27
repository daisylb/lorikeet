from django.conf import settings as s


class Settings:
    _defaults = {
        'subject': "Your order ID {order.invoice_id}",
        'from_address': 'orders@example.com',
        'template_html': None,
        'template_text': None,
        'copy_address': None,
    }

    def __getattr__(self, attr):
        if attr not in self._defaults:
            raise KeyError(attr)
        return getattr(s, 'LORIKEET_EMAIL_INVOICE_' + attr.upper(), self._defaults[attr])

    @property
    def copy_address(self):
        return getattr(s, 'LORIKEET_EMAIL_INVOICE_COPY_ADDRESS', None)


settings = Settings()
__all__ = ['settings']
