from prometheus_client import Counter, Histogram, Gauge
import time
import psutil
import logging

logger = logging.getLogger('sysfree')

# Contador de solicitudes HTTP
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total de solicitudes HTTP procesadas',
    ['method', 'endpoint', 'status_code']
)

# Histograma de latencia de solicitudes HTTP (en segundos)
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'Duración de las solicitudes HTTP',
    ['method', 'endpoint']
)

# Contador de consultas a la base de datos
DB_QUERY_COUNT = Counter(
    'db_query_total',
    'Total de consultas ejecutadas en la base de datos',
    ['query_type']
)

# Histograma de latencia de consultas a la base de datos
DB_QUERY_LATENCY = Histogram(
    'db_query_duration_seconds',
    'Duración de las consultas a la base de datos',
    ['query_type'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0)
)

# Métricas del sistema
MEMORY_USAGE = Gauge(
    'memory_usage_bytes',
    'Uso de memoria del proceso en bytes'
)

CPU_USAGE = Gauge(
    'cpu_usage_percent',
    'Uso de CPU del sistema en porcentaje'
)

# Contador de tareas de Celery
CELERY_TASK_COUNT = Counter(
    'celery_task_total',
    'Total de tareas de Celery procesadas',
    ['task_name', 'status']
)

# Histograma de latencia de tareas de Celery
CELERY_TASK_LATENCY = Histogram(
    'celery_task_duration_seconds',
    'Duración de las tareas de Celery',
    ['task_name'],
    buckets=(0.01, 0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0, 600.0)
)

def update_system_metrics():
    """
    Actualiza las métricas del sistema: uso de memoria y CPU.
    Registra errores si psutil falla.
    """
    try:
        MEMORY_USAGE.set(psutil.virtual_memory().used)
        CPU_USAGE.set(psutil.cpu_percent())
    except Exception as e:
        logger.error(f"Error actualizando métricas del sistema: {str(e)}")

def timing_decorator(func):
    """
    Decorador para medir el tiempo de ejecución de funciones y registrar
    la latencia en Prometheus.
    """
    FUNCTION_LATENCY = Histogram(
        'function_duration_seconds',
        'Duración de ejecución de funciones decoradas',
        ['function_name']
    )
    
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        FUNCTION_LATENCY.labels(function_name=func.__name__).observe(duration)
        return result
    return wrapper