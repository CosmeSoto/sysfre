from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Administración del Sistema'

    def ready(self):
        import core.signals  # Importamos las señales al iniciar la aplicación
        import core.mixins.auditoria_mixins  # Importamos las señales de auditoría de autenticación