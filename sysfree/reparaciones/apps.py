from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ReparacionesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reparaciones'
    verbose_name = _('Reparaciones')
    
    def ready(self):
        import reparaciones.signals  # Señales específicas de reparaciones