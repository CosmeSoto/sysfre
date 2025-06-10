"""
Servicio para gestionar la configuración del sistema.
"""
from django.core.cache import cache
from ..models import ConfiguracionSistema
from .iva_service import IVAService


class ConfiguracionService:
    """Servicio para gestionar la configuración del sistema."""
    
    CACHE_KEY = 'configuracion_sistema'
    CACHE_TIMEOUT = 3600  # 1 hora
    
    @classmethod
    def get_configuracion(cls):
        """
        Obtiene la configuración del sistema.
        
        Returns:
            ConfiguracionSistema: La configuración del sistema o None si no existe.
        """
        # Intentar obtener del cache primero
        configuracion = cache.get(cls.CACHE_KEY)
        
        if configuracion is None:
            try:
                configuracion = ConfiguracionSistema.objects.first()
                if configuracion is None:
                    # Si no hay configuración, crear una por defecto
                    configuracion = ConfiguracionSistema.objects.create()
                
                # Guardar en cache
                cache.set(cls.CACHE_KEY, configuracion, cls.CACHE_TIMEOUT)
            except Exception:
                return None
                
        return configuracion
    
    @classmethod
    def get_iva_default(cls):
        """
        Obtiene el tipo de IVA predeterminado desde la configuración del sistema.
        
        Returns:
            TipoIVA: El tipo de IVA predeterminado o None si no existe.
        """
        configuracion = cls.get_configuracion()
        if configuracion and configuracion.tipo_iva_default:
            return configuracion.tipo_iva_default
        
        # Si no hay configuración o no tiene tipo_iva_default, usar el servicio IVA
        return IVAService.get_default()
    
    @classmethod
    def get_iva_porcentaje(cls):
        """
        Obtiene el porcentaje de IVA predeterminado.
        
        Returns:
            Decimal: El porcentaje de IVA predeterminado.
        """
        tipo_iva = cls.get_iva_default()
        if tipo_iva:
            return tipo_iva.porcentaje
        
        # Valor por defecto si no hay tipo_iva
        return 12.00
    
    @classmethod
    def invalidar_cache(cls):
        """Invalida la caché de configuración del sistema."""
        cache.delete(cls.CACHE_KEY)