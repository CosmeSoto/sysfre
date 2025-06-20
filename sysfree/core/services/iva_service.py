"""
Servicio para gestionar los tipos de IVA en toda la aplicación.
Este servicio proporciona métodos para acceder a los tipos de IVA
sin necesidad de configuraciones en settings.
"""
from django.db.models import Q
from ..models.tipo_iva import TipoIVA
from .cache_service import CacheService


class IVAService:
    """Servicio para gestionar los tipos de IVA en toda la aplicación."""
    
    CACHE_TIMEOUT = 7200  # 2 horas
    
    @classmethod
    def get_default(cls):
        """
        Obtiene el tipo de IVA predeterminado.
        
        Returns:
            TipoIVA: El tipo de IVA predeterminado o None si no existe.
        """
        # Intentar obtener del cache primero
        iva_default = CacheService.get_iva('default')
        
        if iva_default is None:
            try:
                iva_default = TipoIVA.objects.filter(es_default=True).first()
                if iva_default is None:
                    iva_default = TipoIVA.objects.first()
                
                if iva_default:
                    CacheService.set_iva('default', iva_default, cls.CACHE_TIMEOUT)
            except Exception:
                return None
                
        return iva_default
    
    @classmethod
    def get_by_id(cls, id):
        """
        Obtiene un tipo de IVA por su ID.
        
        Args:
            id (int): El ID del tipo de IVA.
            
        Returns:
            TipoIVA: El tipo de IVA correspondiente o None si no existe.
        """
        try:
            return TipoIVA.objects.filter(id=id).first()
        except Exception:
            return None
    
    @classmethod
    def get_by_codigo(cls, codigo):
        """
        Obtiene un tipo de IVA por su código.
        
        Args:
            codigo (str): El código del tipo de IVA.
            
        Returns:
            TipoIVA: El tipo de IVA correspondiente o None si no existe.
        """
        try:
            return TipoIVA.objects.filter(codigo=codigo).first()
        except Exception:
            return None
    
    @classmethod
    def get_by_porcentaje(cls, porcentaje):
        """
        Obtiene un tipo de IVA por su porcentaje.
        
        Args:
            porcentaje (Decimal): El porcentaje del tipo de IVA.
            
        Returns:
            TipoIVA: El tipo de IVA correspondiente o None si no existe.
        """
        try:
            return TipoIVA.objects.filter(porcentaje=porcentaje).first()
        except Exception:
            return None
    
    @classmethod
    def get_all(cls):
        """
        Obtiene todos los tipos de IVA.
        
        Returns:
            QuerySet: QuerySet con todos los tipos de IVA.
        """
        # Intentar obtener del cache primero
        tipos_iva = CacheService.get_iva('all')
        
        if tipos_iva is None:
            try:
                tipos_iva = list(TipoIVA.objects.all())
                CacheService.set_iva('all', tipos_iva, cls.CACHE_TIMEOUT)
            except Exception:
                return []
                
        return tipos_iva
    
    @classmethod
    def calcular_iva(cls, base_imponible, tipo_iva=None):
        """
        Calcula el IVA para un monto dado.
        
        Args:
            base_imponible (Decimal): El monto base imponible.
            tipo_iva (TipoIVA, optional): El tipo de IVA a aplicar. 
                                         Si es None, se usa el predeterminado.
        
        Returns:
            tuple: (monto_iva, total_con_iva)
        """
        if tipo_iva is None:
            tipo_iva = cls.get_default()
            
        if tipo_iva is None or base_imponible is None:
            return 0, base_imponible
            
        monto_iva = base_imponible * (tipo_iva.porcentaje / 100)
        total = base_imponible + monto_iva
        
        return monto_iva, total
    
    @classmethod
    def invalidar_cache(cls):
        """Invalida la caché de tipos de IVA."""
        CacheService.invalidate_iva()