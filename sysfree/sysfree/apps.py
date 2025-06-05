from django.apps import AppConfig


class SysfreeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sysfree'
    verbose_name = 'SysFree'

    def ready(self):
        """
        Método ejecutado cuando la aplicación está lista.
        Inicia servicios como el monitoreo del sistema.
        """
        # Importar aquí para evitar problemas de importación circular
        import logging
        logger = logging.getLogger('sysfree')
        
        # Solo iniciar el monitoreo en el proceso principal
        import os
        if os.environ.get('RUN_MAIN', None) != 'true':
            try:
                from core.monitoring import start_monitoring
                start_monitoring()
                logger.info("Sistema de monitoreo iniciado correctamente")
            except Exception as e:
                logger.error(f"Error al iniciar el sistema de monitoreo: {str(e)}")