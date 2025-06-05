from django.core.cache import cache


class CacheService:
    """Servicio para gestionar la caché del sistema."""
    
    @classmethod
    def get(cls, key, default=None):
        """
        Obtiene un valor de la caché.
        
        Args:
            key: Clave del valor
            default: Valor por defecto si no existe
            
        Returns:
            El valor almacenado o el valor por defecto
        """
        return cache.get(key, default)
    
    @classmethod
    def set(cls, key, value, timeout=3600):
        """
        Establece un valor en la caché.
        
        Args:
            key: Clave del valor
            value: Valor a almacenar
            timeout: Tiempo de expiración en segundos (por defecto 1 hora)
            
        Returns:
            None
        """
        cache.set(key, value, timeout)
    
    @classmethod
    def delete(cls, key):
        """
        Elimina un valor de la caché.
        
        Args:
            key: Clave del valor
            
        Returns:
            None
        """
        cache.delete(key)
    
    @classmethod
    def clear(cls):
        """
        Limpia toda la caché.
        
        Returns:
            None
        """
        cache.clear()
    
    @classmethod
    def get_or_set(cls, key, default_func, timeout=3600):
        """
        Obtiene un valor de la caché o lo establece si no existe.
        
        Args:
            key: Clave del valor
            default_func: Función que devuelve el valor por defecto
            timeout: Tiempo de expiración en segundos
            
        Returns:
            El valor almacenado o el resultado de default_func
        """
        return cache.get_or_set(key, default_func, timeout)