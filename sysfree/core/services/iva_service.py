"""
Servicio para gestionar los tipos de IVA en toda la aplicación.
Este servicio proporciona métodos para acceder a los tipos de IVA
sin necesidad de configuraciones en settings.
"""
from django.core.cache import cache
from django.db.models import Q
from ..models.tipo_iva import TipoIVA


class IVAService:
    """Servicio para gestionar los tipos de IVA en toda la aplicación."""
    
    CACHE_KEY_DEFAULT = 'tipo_iva_default'
    CACHE_KEY_ALL = 'tipos_iva_all'
    CACHE_TIMEOUT = 3600  # 1 hora
    
    @classmethod
    def get_default(cls):
        """
        Obtiene el tipo de IVA predeterminado.
        
        Returns:
            TipoIVA: El tipo de IVA predeterminado o None si no existe.
        """
        # Intentar obtener del cache primero
        iva_default = cache.get(cls.CACHE_KEY_DEFAULT)
        
        if iva_default is None:
            try:
                iva_default = TipoIVA.objects.filter(es_default=True).first()
                if iva_default is None:
                    # Si no hay un IVA predeterminado, intentar obtener cualquier IVA
                    iva_default = TipoIVA.objects.first()
                
                # Guardar en cache si existe
                if iva_default:
                    cache.set(cls.CACHE_KEY_DEFAULT, iva_default, cls.CACHE_TIMEOUT)
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
        tipos_iva = cache.get(cls.CACHE_KEY_ALL)
        
        if tipos_iva is None:
            try:
                tipos_iva = TipoIVA.objects.all()
                # Guardar en cache
                cache.set(cls.CACHE_KEY_ALL, tipos_iva, cls.CACHE_TIMEOUT)
            except Exception:
                return TipoIVA.objects.none()
                
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
        cache.delete(cls.CACHE_KEY_DEFAULT)
        cache.delete(cls.CACHE_KEY_ALL)