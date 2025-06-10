"""
Context processors para la aplicación core.
Estos procesadores añaden variables al contexto de las plantillas.
"""
from .services import IVAService


def iva_context_processor(request):
    """
    Añade información sobre los tipos de IVA al contexto de las plantillas.
    
    Args:
        request: La solicitud HTTP.
        
    Returns:
        dict: Diccionario con información de IVA para las plantillas.
    """
    iva_default = IVAService.get_default()
    tipos_iva = IVAService.get_all()
    
    return {
        'iva_default': iva_default,
        'tipos_iva': tipos_iva,
    }