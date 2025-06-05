from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class FiscalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fiscal'
    verbose_name = _('Gestión Fiscal')

    def ready(self):
        import fiscal.signals  # Importamos las señales al iniciar la aplicación