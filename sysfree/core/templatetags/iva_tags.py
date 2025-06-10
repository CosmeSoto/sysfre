"""
Template tags para trabajar con IVA en las plantillas.
"""
from django import template
from decimal import Decimal
from ..services import IVAService

register = template.Library()


@register.simple_tag
def get_iva_default():
    """
    Obtiene el tipo de IVA predeterminado.
    
    Returns:
        TipoIVA: El tipo de IVA predeterminado.
    """
    return IVAService.get_default()


@register.simple_tag
def get_iva_by_codigo(codigo):
    """
    Obtiene un tipo de IVA por su código.
    
    Args:
        codigo (str): El código del tipo de IVA.
        
    Returns:
        TipoIVA: El tipo de IVA correspondiente.
    """
    return IVAService.get_by_codigo(codigo)


@register.simple_tag
def calcular_iva(base_imponible, tipo_iva=None):
    """
    Calcula el IVA para un monto dado.
    
    Args:
        base_imponible (Decimal): El monto base imponible.
        tipo_iva (TipoIVA, optional): El tipo de IVA a aplicar.
        
    Returns:
        tuple: (monto_iva, total_con_iva)
    """
    return IVAService.calcular_iva(base_imponible, tipo_iva)


@register.filter
def aplicar_iva(base_imponible):
    """
    Aplica el IVA predeterminado a un monto y devuelve el total.
    
    Args:
        base_imponible (Decimal): El monto base imponible.
        
    Returns:
        Decimal: El total con IVA.
    """
    _, total = IVAService.calcular_iva(base_imponible)
    return total


@register.filter
def monto_iva(base_imponible):
    """
    Calcula el monto de IVA para un monto dado usando el IVA predeterminado.
    
    Args:
        base_imponible (Decimal): El monto base imponible.
        
    Returns:
        Decimal: El monto de IVA.
    """
    monto, _ = IVAService.calcular_iva(base_imponible)
    return monto


@register.filter
def porcentaje_iva_default(formato=True):
    """
    Obtiene el porcentaje del IVA predeterminado.
    
    Args:
        formato (bool): Si es True, devuelve el porcentaje con el símbolo %.
        
    Returns:
        str or Decimal: El porcentaje del IVA predeterminado.
    """
    iva = IVAService.get_default()
    if not iva:
        return "0%" if formato else Decimal('0')
    
    if formato:
        return f"{iva.porcentaje}%"
    return iva.porcentaje