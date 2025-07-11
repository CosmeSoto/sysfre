from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class EcommerceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ecommerce'
    verbose_name = _('Comercio Electrónico')
    
    def ready(self):
        import ecommerce.signals  # Señales específicas de ecommerce