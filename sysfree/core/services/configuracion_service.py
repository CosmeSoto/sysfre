from django.core.cache import cache
from ..models import ConfiguracionSistema


class ConfiguracionService:
    """Servicio para gestionar las configuraciones del sistema."""
    
    CACHE_PREFIX = 'config_'
    CACHE_TIMEOUT = 3600  # 1 hora
    
    @classmethod
    def get_configuracion(cls):
        """
        Obtiene la configuración del sistema.
        Primero busca en caché, si no existe, busca en la base de datos.
        """
        cache_key = f"{cls.CACHE_PREFIX}sistema"
        config_cache = cache.get(cache_key)
        
        if config_cache is not None:
            return config_cache
        
        try:
            config = ConfiguracionSistema.objects.first()
            if not config:
                config = ConfiguracionSistema.objects.create()
            
            cache.set(cache_key, config, cls.CACHE_TIMEOUT)
            return config
        except Exception:
            return ConfiguracionSistema()
    
    @classmethod
    def actualizar_configuracion(cls, datos):
        """
        Actualiza la configuración del sistema.
        
        Args:
            datos: Diccionario con los datos a actualizar
            
        Returns:
            ConfiguracionSistema: La configuración actualizada
        """
        config = cls.get_configuracion()
        
        for campo, valor in datos.items():
            if hasattr(config, campo):
                setattr(config, campo, valor)
        
        config.save()
        
        # Actualizar caché
        cache_key = f"{cls.CACHE_PREFIX}sistema"
        cache.set(cache_key, config, cls.CACHE_TIMEOUT)
        
        return config
    
    @classmethod
    def limpiar_cache(cls):
        """Limpia la caché de configuración."""
        cache_key = f"{cls.CACHE_PREFIX}sistema"
        cache.delete(cache_key)