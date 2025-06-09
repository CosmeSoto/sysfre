from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class InventarioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventario'
    verbose_name = _('Inventario')
    
    def ready(self):
        import inventario.signals 