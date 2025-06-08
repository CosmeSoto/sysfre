import logging
from django.utils import timezone
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from ventas.services.venta_service import VentaService
from inventario.models import Producto
from core.log_utils import log_function_call
from reparaciones.models import Reparacion

logger = logging.getLogger('sysfree')

class ReparacionVentaService:
    """Servicio para gestionar proformas de reparaciones usando Venta."""
    
    @classmethod
    @log_function_call
    @transaction.atomic
    def crear_proforma_reparacion(cls, reparacion, items=None, usuario=None):
        """
        Crea una proforma para una reparación usando el modelo Venta.
        
        Args:
            reparacion: Reparación para la que se crea la proforma
            items: Lista de diccionarios con producto_id, cantidad, precio_unitario, descuento
                  Si es None, se usarán los repuestos de la reparación
            usuario: Usuario que crea la proforma
            
        Returns:
            Venta: La proforma creada (Venta con tipo='proforma')
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
                try:
                    servicio = Producto.objects.filter(tipo='servicio').first()
                    if servicio:
                        items.append({
                            'producto_id': servicio.id,
                            'cantidad': 1,
                            'precio_unitario': reparacion.costo_estimado or 0,
                            'descuento': 0
                        })
                except Producto.DoesNotExist:
                    pass
        
        # Si no hay items, no se puede crear la proforma
        if not items:
            raise ValueError(_("No hay items para crear la proforma"))
        
        # Crear la proforma usando VentaService
        proforma = VentaService.crear_venta(
            cliente=reparacion.cliente,
            tipo='proforma',
            items=items,
            reparacion=reparacion,
            notas=f"Proforma para reparación #{reparacion.numero} - {reparacion.tipo_equipo} {reparacion.marca} {reparacion.modelo}",
            usuario=usuario
        )
        
        logger.info(f"Proforma {proforma.numero} creada para reparación {reparacion.numero}")
        
        return proforma