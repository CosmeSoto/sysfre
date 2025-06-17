from celery import shared_task
from sysfree.monitoring import update_system_metrics

@shared_task
def update_system_metrics_task():
    """
    Tarea periódica que actualiza las métricas del sistema (CPU y memoria) para Prometheus.
    """
    update_system_metrics()