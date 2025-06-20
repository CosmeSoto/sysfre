from django.core.cache import cache


class CacheService:
    """Servicio para gestionar la caché Redis del sistema."""
    
    @classmethod
    def get(cls, key, default=None):
        return cache.get(key, default)
    
    @classmethod
    def set(cls, key, value, timeout=3600):
        cache.set(key, value, timeout)
    
    @classmethod
    def delete(cls, key):
        cache.delete(key)
    
    @classmethod
    def delete_pattern(cls, pattern):
        """Elimina claves que coincidan con un patrón (Redis)."""
        cache.delete_pattern(pattern)
    
    @classmethod
    def get_or_set(cls, key, default_func, timeout=3600):
        return cache.get_or_set(key, default_func, timeout)
    
    # Métodos específicos para IVA
    @classmethod
    def get_iva(cls, key, default=None):
        return cls.get(f"iva_{key}", default)
    
    @classmethod
    def set_iva(cls, key, value, timeout=7200):
        cls.set(f"iva_{key}", value, timeout)
    
    @classmethod
    def invalidate_iva(cls):
        cls.delete_pattern("iva_*")