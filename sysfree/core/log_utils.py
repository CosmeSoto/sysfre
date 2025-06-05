import logging
import time
import functools

# Configurar logger
logger = logging.getLogger('sysfree')

def log_function_call(func):
    """
    Decorador para registrar llamadas a funciones.
    Registra el inicio y fin de la función, así como el tiempo de ejecución.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger.info(f"Iniciando {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            logger.info(f"Finalizado {func.__name__} en {elapsed_time:.3f}s")
            return result
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"Error en {func.__name__} después de {elapsed_time:.3f}s: {str(e)}")
            raise
    
    return wrapper

def log_critical_operation(operation_name):
    """
    Registra una operación crítica en el sistema.
    
    Args:
        operation_name: Nombre de la operación
    """
    logger.critical(f"OPERACIÓN CRÍTICA: {operation_name}")

def log_security_event(event_type, user=None, details=None):
    """
    Registra un evento de seguridad.
    
    Args:
        event_type: Tipo de evento (login, logout, acceso_denegado, etc.)
        user: Usuario relacionado con el evento
        details: Detalles adicionales
    """
    security_logger = logging.getLogger('django.security')
    
    user_info = f"Usuario: {user}" if user else "Usuario: Anónimo"
    details_info = f" - Detalles: {details}" if details else ""
    
    security_logger.info(f"Evento de seguridad: {event_type} - {user_info}{details_info}")

def log_database_operation(operation, model, object_id=None):
    """
    Registra una operación en la base de datos.
    
    Args:
        operation: Tipo de operación (crear, actualizar, eliminar)
        model: Modelo afectado
        object_id: ID del objeto afectado
    """
    db_logger = logging.getLogger('django.db.backends')
    
    object_info = f" - ID: {object_id}" if object_id else ""
    db_logger.info(f"Operación en BD: {operation} - Modelo: {model}{object_info}")