"""
Servicio para gestionar la información de la empresa.
"""
from django.core.cache import cache
from ..models import Empresa


class EmpresaService:
    """Servicio para gestionar la información de la empresa."""
    
    CACHE_KEY = 'empresa_principal'
    CACHE_TIMEOUT = 3600  # 1 hora
    
    @classmethod
    def get_empresa(cls):
        """
        Obtiene la empresa principal del sistema.
        
        Returns:
            Empresa: La empresa principal o None si no existe.
        """
        # Intentar obtener del cache primero
        empresa = cache.get(cls.CACHE_KEY)
        
        if empresa is None:
            try:
                empresa = Empresa.objects.first()
                if empresa:
                    # Guardar en cache
                    cache.set(cls.CACHE_KEY, empresa, cls.CACHE_TIMEOUT)
            except Exception:
                return None
                
        return empresa
    
    @classmethod
    def get_nombre_empresa(cls):
        """
        Obtiene el nombre de la empresa.
        
        Returns:
            str: El nombre de la empresa o un valor por defecto.
        """
        empresa = cls.get_empresa()
        return empresa.nombre if empresa else 'SysFree'
    
    @classmethod
    def get_ruc_empresa(cls):
        """
        Obtiene el RUC de la empresa.
        
        Returns:
            str: El RUC de la empresa o cadena vacía.
        """
        empresa = cls.get_empresa()
        return empresa.ruc if empresa else ''
    
    @classmethod
    def get_ambiente_facturacion(cls):
        """
        Obtiene el ambiente de facturación configurado.
        
        Returns:
            str: '1' para pruebas, '2' para producción.
        """
        empresa = cls.get_empresa()
        return empresa.ambiente_facturacion if empresa else '1'
    
    @classmethod
    def get_urls_sri(cls):
        """
        Obtiene las URLs del SRI según el ambiente configurado.
        
        Returns:
            dict: Diccionario con las URLs de recepción y autorización.
        """
        empresa = cls.get_empresa()
        if not empresa:
            return {
                'recepcion': 'https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl',
                'autorizacion': 'https://celcer.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl'
            }
        
        if empresa.ambiente_facturacion == '2':  # Producción
            return {
                'recepcion': empresa.url_recepcion_produccion,
                'autorizacion': empresa.url_autorizacion_produccion
            }
        else:  # Pruebas
            return {
                'recepcion': empresa.url_recepcion_pruebas,
                'autorizacion': empresa.url_autorizacion_pruebas
            }
    
    @classmethod
    def invalidar_cache(cls):
        """Invalida la caché de la empresa."""
        cache.delete(cls.CACHE_KEY)