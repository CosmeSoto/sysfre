"""
Utilidades para trabajar con IVA en toda la aplicación.
Estas funciones son helpers que utilizan el IVAService internamente.
"""
from decimal import Decimal
from ..services import IVAService


def aplicar_iva_default(base_imponible):
    """
    Aplica el IVA predeterminado a un monto.
    
    Args:
        base_imponible (Decimal): El monto base imponible.
        
    Returns:
        tuple: (monto_iva, total_con_iva)
    """
    return IVAService.calcular_iva(base_imponible)


def aplicar_iva_por_codigo(base_imponible, codigo_iva):
    """
    Aplica un IVA específico por su código a un monto.
    
    Args:
        base_imponible (Decimal): El monto base imponible.
        codigo_iva (str): El código del tipo de IVA a aplicar.
        
    Returns:
        tuple: (monto_iva, total_con_iva)
    """
    tipo_iva = IVAService.get_by_codigo(codigo_iva)
    return IVAService.calcular_iva(base_imponible, tipo_iva)


def aplicar_iva_por_porcentaje(base_imponible, porcentaje):
    """
    Aplica un IVA específico por su porcentaje a un monto.
    
    Args:
        base_imponible (Decimal): El monto base imponible.
        porcentaje (Decimal): El porcentaje del tipo de IVA a aplicar.
        
    Returns:
        tuple: (monto_iva, total_con_iva)
    """
    tipo_iva = IVAService.get_by_porcentaje(porcentaje)
    return IVAService.calcular_iva(base_imponible, tipo_iva)


def get_iva_default_info():
    """
    Obtiene información del IVA predeterminado.
    
    Returns:
        dict: Diccionario con información del IVA predeterminado.
    """
    iva = IVAService.get_default()
    if not iva:
        return {
            'nombre': 'No configurado',
            'codigo': 'N/A',
            'porcentaje': Decimal('0.00')
        }
    
    return {
        'nombre': iva.nombre,
        'codigo': iva.codigo,
        'porcentaje': iva.porcentaje
    }


def get_all_ivas_info():
    """
    Obtiene información de todos los tipos de IVA disponibles.
    
    Returns:
        list: Lista de diccionarios con información de cada tipo de IVA.
    """
    ivas = IVAService.get_all()
    return [
        {
            'id': iva.id,
            'nombre': iva.nombre,
            'codigo': iva.codigo,
            'porcentaje': iva.porcentaje,
            'es_default': iva.es_default
        }
        for iva in ivas
    ]