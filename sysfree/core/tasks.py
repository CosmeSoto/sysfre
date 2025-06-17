from celery import shared_task
from sysfree.monitoring import update_system_metrics, CELERY_TASK_LATENCY, CELERY_TASK_COUNT

@shared_task
def update_system_metrics_task():
    """
    Tarea periódica que actualiza las métricas del sistema (CPU y memoria) para Prometheus
    y registra su duración.
    """
    import time
    start_time = time.time()
    try:
        update_system_metrics()
        duration = time.time() - start_time
        CELERY_TASK_LATENCY.labels(task_name="update_system_metrics_task").observe(duration)
        CELERY_TASK_COUNT.labels(task_name="update_system_metrics_task", status="SUCCESS").inc()
    except Exception as e:
        CELERY_TASK_COUNT.labels(task_name="update_system_metrics_task", status="FAILURE").inc()
        raise