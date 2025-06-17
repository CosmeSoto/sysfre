from django.apps import AppConfig
from django.conf import settings
import os

class SysfreeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sysfree'
    verbose_name = 'SysFree'

    def ready(self):
        """
        Método ejecutado al inicializar la aplicación.
        Inicia el sistema de monitoreo (definido en core.monitoring) solo en el
        proceso principal, si está habilitado en la configuración.
        """
        import logging
        logger = logging.getLogger('sysfree')

        # Iniciar monitoreo solo en el proceso principal y si está habilitado
        if os.environ.get('RUN_MAIN') and getattr(settings, 'ENABLE_SYSTEM_MONITORING', True):
            try:
                from core.monitoring import start_monitoring
                start_monitoring()
                logger.info("Sistema de monitoreo iniciado correctamente")
            except (ImportError, RuntimeError) as e:
                logger.error(f"Error al iniciar el sistema de monitoreo: {str(e)}")