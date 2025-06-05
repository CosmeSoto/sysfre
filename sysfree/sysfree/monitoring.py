from prometheus_client import Counter, Histogram, Gauge
import time
import psutil
import os

# Métricas para solicitudes HTTP
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total de solicitudes HTTP',
    ['method', 'endpoint', 'status_code']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'Duración de las solicitudes HTTP',
    ['method', 'endpoint'],
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0)
)

# Métricas para la base de datos
DB_QUERY_COUNT = Counter(
    'db_query_total',
    'Total de consultas a la base de datos',
    ['query_type']
)

DB_QUERY_LATENCY = Histogram(
    'db_query_duration_seconds',
    'Duración de las consultas a la base de datos',
    ['query_type'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0)
)

# Métricas para el sistema
MEMORY_USAGE = Gauge(
    'memory_usage_bytes',
    'Uso de memoria en bytes'
)

CPU_USAGE = Gauge(
    'cpu_usage_percent',
    'Uso de CPU en porcentaje'
)

# Métricas para Celery
CELERY_TASK_COUNT = Counter(
    'celery_task_total',
    'Total de tareas de Celery',
    ['task_name', 'status']
)

CELERY_TASK_LATENCY = Histogram(
    'celery_task_duration_seconds',
    'Duración de las tareas de Celery',
    ['task_name'],
    buckets=(0.01, 0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0, 600.0)
)

# Función para actualizar métricas del sistema
def update_system_metrics():
    MEMORY_USAGE.set(psutil.virtual_memory().used)
    CPU_USAGE.set(psutil.cpu_percent())

# Decorador para medir el tiempo de ejecución de funciones
def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        
        # Aquí se pueden registrar métricas específicas para la función
        # Ejemplo: FUNCTION_LATENCY.labels(func.__name__).observe(duration)
        
        return result
    return wrapper