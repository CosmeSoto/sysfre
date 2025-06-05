import os
import psutil
import logging
import time
import threading
from django.conf import settings

# Configurar logger
logger = logging.getLogger('sysfree.monitoring')

class SystemMonitor:
    """
    Clase para monitorear el sistema y registrar métricas.
    """
    
    def __init__(self, interval=300):  # 5 minutos por defecto
        self.interval = interval
        self.running = False
        self.thread = None
    
    def start(self):
        """Inicia el monitoreo en un hilo separado."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop)
        self.thread.daemon = True
        self.thread.start()
        logger.info("Sistema de monitoreo iniciado")
    
    def stop(self):
        """Detiene el monitoreo."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        logger.info("Sistema de monitoreo detenido")
    
    def _monitor_loop(self):
        """Bucle principal de monitoreo."""
        while self.running:
            try:
                self._collect_metrics()
            except Exception as e:
                logger.error(f"Error al recolectar métricas: {str(e)}")
            
            time.sleep(self.interval)
    
    def _collect_metrics(self):
        """Recolecta y registra métricas del sistema."""
        # Uso de CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Uso de memoria
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used_mb = memory.used / (1024 * 1024)  # Convertir a MB
        
        # Uso de disco
        disk = psutil.disk_usage(os.path.dirname(settings.BASE_DIR))
        disk_percent = disk.percent
        disk_free_gb = disk.free / (1024 * 1024 * 1024)  # Convertir a GB
        
        # Registrar métricas
        logger.info(f"Métricas del sistema - CPU: {cpu_percent}%, "
                   f"Memoria: {memory_percent}% ({memory_used_mb:.1f} MB), "
                   f"Disco: {disk_percent}% (Libre: {disk_free_gb:.1f} GB)")

# Instancia global del monitor
system_monitor = SystemMonitor()

def start_monitoring():
    """Inicia el sistema de monitoreo."""
    system_monitor.start()

def stop_monitoring():
    """Detiene el sistema de monitoreo."""
    system_monitor.stop()

def get_system_status():
    """
    Obtiene el estado actual del sistema.
    
    Returns:
        dict: Diccionario con métricas del sistema
    """
    try:
        return {
            'cpu_percent': psutil.cpu_percent(interval=0.5),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage(os.path.dirname(settings.BASE_DIR)).percent,
        }
    except Exception as e:
        logger.error(f"Error al obtener estado del sistema: {str(e)}")
        return {
            'error': str(e)
        }