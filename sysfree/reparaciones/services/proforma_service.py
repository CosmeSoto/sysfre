import logging
from django.utils import timezone
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from ventas.models import Proforma
from ventas.services.proforma_service import ProformaService
from inventario.models import Producto
from core.log_utils import log_function_call

# Configurar logger
logger = logging.getLogger('sysfree')

class ReparacionProformaService:
    """Servicio para gestionar proformas de reparaciones."""
    
    @classmethod
    @log_function_call
    @transaction.atomic
    def crear_proforma_reparacion(cls, reparacion, items=None, usuario=None):
        """
        Crea una proforma para una reparación.
        
        Args:
            reparacion: Reparación para la que se crea la proforma
            items: Lista de diccionarios con producto_id, cantidad, precio_unitario, descuento
                  Si es None, se usarán los repuestos de la reparación
            usuario: Usuario que crea la proforma
            
        Returns:
            Proforma: La proforma creada
        """
        # Si no se proporcionan items, usar los repuestos de la reparación
        if items is None:
            items = []
            for repuesto in reparacion.repuestos.all():
                items.append({
                    'producto_id': repuesto.producto.id,
                    'cantidad': repuesto.cantidad,
                    'precio_unitario': repuesto.precio_unitario,
                    'descuento': 0
                })
            
            # Si no hay repuestos, agregar un item para el servicio de reparación
            if not items:
                # Buscar un producto de tipo servicio para la reparación
                try:
                    servicio = Producto.objects.filter(tipo='servicio').first()
                    if servicio:
                        items.append({
                            'producto_id': servicio.id,
                            'cantidad': 1,
                            'precio_unitario': reparacion.costo_estimado,
                            'descuento': 0
                        })
                except Producto.DoesNotExist:
                    pass
        
        # Si no hay items, no se puede crear la proforma
        if not items:
            raise ValueError(_("No hay items para crear la proforma"))
        
        # Crear la proforma
        proforma = ProformaService.crear_proforma(
            cliente=reparacion.cliente,
            items=items,
            reparacion=reparacion,
            notas=f"Proforma para reparación #{reparacion.numero} - {reparacion.tipo_equipo} {reparacion.marca} {reparacion.modelo}",
            usuario=usuario
        )
        
        logger.info(f"Proforma {proforma.numero} creada para reparación {reparacion.numero}")
        
        return proforma