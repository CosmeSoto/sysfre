from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ClientesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'clientes'
    verbose_name = _('Clientes')

    def ready(self):
        pass  # Las señales de auditoría están en core.signals