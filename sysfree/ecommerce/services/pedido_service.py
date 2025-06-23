from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from ..models import Pedido, DetallePedido
from reparaciones.models import Reparacion, ServicioReparacion
from inventario.models import Producto
from core.services.cache_service import CacheService
from core.services.auditoria_service import AuditoriaService
import uuid
import logging

logger = logging.getLogger('sysfree')


class PedidoService:
    """Servicio para gestionar pedidos en la tienda online."""
    
    @classmethod
    def invalidar_cache_pedido(cls, pedido_id=None):
        """Invalida el caché relacionado con pedidos."""
        try:
            CacheService.delete('pedidos_list')
            if pedido_id:
                CacheService.delete_pattern(f'*pedido*{pedido_id}*')
        except Exception as e:
            logger.error(f"Error al invalidar caché de pedido: {str(e)}")
    
    @staticmethod
    @transaction.atomic
    def crear_pedido_desde_carrito(carrito, direccion_facturacion, direccion_envio, notas=''):
        """
        Crea un nuevo pedido a partir de un carrito de compra.
        
        Args:
            carrito: Objeto Carrito
            direccion_facturacion: Objeto DireccionCliente para facturación
            direccion_envio: Objeto DireccionCliente para envío
            notas: Notas adicionales del pedido
            
        Returns:
            Objeto Pedido creado
        """
        if not carrito.items.exists():
            raise ValueError(_("El carrito está vacío"))
        
        # Validar stock
        from .stock_validation_service import StockValidationService
        stock_valido, productos_sin_stock = StockValidationService.validar_stock_carrito(carrito)
        
        if not stock_valido:
            productos_str = ", ".join([f"{p['producto'].nombre} (solicitado: {p['cantidad_solicitada']}, disponible: {p['stock_actual']})" for p in productos_sin_stock])
            raise ValueError(_("No hay suficiente stock para los siguientes productos: {}").format(productos_str))
        
        # Generar número de pedido único
        numero_pedido = f"PED-{uuid.uuid4().hex[:8].upper()}"
        
        # Crear el pedido
        pedido = Pedido.objects.create(
            numero=numero_pedido,
            cliente=carrito.cliente,
            carrito=carrito,
            direccion_facturacion=direccion_facturacion,
            direccion_envio=direccion_envio,
            notas=notas,
            subtotal=carrito.subtotal,
            impuestos=carrito.total_impuestos,
            total=carrito.total
        )
        
        # Crear detalles del pedido
        for item in carrito.items.all():
            detalle = DetallePedido(
                pedido=pedido,
                cantidad=item.cantidad,
                precio_unitario=item.precio_unitario,
                impuesto_unitario=item.impuesto_unitario,
                subtotal=item.subtotal,
                impuestos=item.impuestos,
                total=item.total,
                es_servicio=item.es_servicio
            )
            
            if item.es_servicio:
                # Es un servicio
                servicio_ct = ContentType.objects.get_for_model(ServicioReparacion)
                detalle.content_type = servicio_ct
                detalle.object_id = item.object_id
                
                # Crear ticket de reparación si es un servicio
                PedidoService._crear_ticket_reparacion(detalle, item, pedido)
            else:
                # Es un producto
                producto_ct = ContentType.objects.get_for_model(Producto)
                detalle.content_type = producto_ct
                detalle.object_id = item.object_id
                detalle.producto = item.producto
            
            detalle.save()
        
        # Marcar el carrito como convertido a pedido
        carrito.convertido_a_pedido = True
        carrito.save()
        
        # Registrar auditoría
        AuditoriaService.registrar_actividad_personalizada(
            accion="PEDIDO_CREADO",
            descripcion=f"Pedido creado desde carrito: {numero_pedido}",
            modelo="Pedido",
            objeto_id=pedido.id,
            datos={'numero': numero_pedido, 'cliente': str(carrito.cliente), 'total': str(pedido.total)}
        )
        
        # Invalidar caché
        PedidoService.invalidar_cache_pedido()
        
        logger.info(f"Pedido {numero_pedido} creado para cliente {carrito.cliente}")
        return pedido
    
    @staticmethod
    def _crear_ticket_reparacion(detalle, item, pedido):
        """
        Crea un ticket de reparación a partir de un item de servicio.
        
        Args:
            detalle: Objeto DetallePedido
            item: Objeto ItemCarrito
            pedido: Objeto Pedido
        """
        servicio = item.item
        
        # Generar número de reparación único
        numero_reparacion = f"REP-{uuid.uuid4().hex[:8].upper()}"
        
        # Crear la reparación
        reparacion = Reparacion.objects.create(
            numero=numero_reparacion,
            cliente=pedido.cliente,
            tipo_equipo="Pendiente de especificar",
            marca="Pendiente de especificar",
            modelo="Pendiente de especificar",
            problema_reportado=f"Servicio solicitado: {servicio.nombre}",
            estado='recibido',
            costo_diagnostico=0,
            costo_reparacion=item.precio_unitario,
            total=item.total,
            creado_por=None  # Se asignará cuando un técnico tome el caso
        )
        
        # Asociar la reparación al detalle del pedido
        detalle.reparacion = reparacion
        
        logger.info(f"Ticket de reparación {numero_reparacion} creado desde pedido {pedido.numero}")
        return reparacion
    
    @staticmethod
    @transaction.atomic
    def actualizar_estado_pedido(pedido, nuevo_estado):
        """
        Actualiza el estado de un pedido.
        
        Args:
            pedido: Objeto Pedido
            nuevo_estado: Nuevo estado del pedido
            
        Returns:
            Objeto Pedido actualizado
        """
        estados_validos = dict(Pedido.ESTADO_CHOICES).keys()
        if nuevo_estado not in estados_validos:
            raise ValueError(f"Estado no válido. Debe ser uno de: {', '.join(estados_validos)}")
        
        # Actualizar campos según el estado
        if nuevo_estado == 'pagado' and pedido.estado != 'pagado':
            pedido.fecha_pago = timezone.now()
        elif nuevo_estado == 'enviado' and pedido.estado != 'enviado':
            pedido.fecha_envio = timezone.now()
        elif nuevo_estado == 'entregado' and pedido.estado != 'entregado':
            pedido.fecha_entrega = timezone.now()
        
        pedido.estado = nuevo_estado
        pedido.save()
        
        # Registrar auditoría
        AuditoriaService.registrar_actividad_personalizada(
            accion="CAMBIO_ESTADO_PEDIDO",
            descripcion=f"Pedido {pedido.numero} cambió a estado {nuevo_estado}",
            modelo="Pedido",
            objeto_id=pedido.id,
            datos={'estado_nuevo': nuevo_estado}
        )
        
        # Invalidar caché
        PedidoService.invalidar_cache_pedido(pedido.id)
        
        logger.info(f"Pedido {pedido.numero} actualizado a estado {nuevo_estado}")
        return pedido