import logging
from django.utils import timezone
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from ventas.models import Proforma, DetalleProforma
from inventario.models import Producto
from core.log_utils import log_function_call

# Configurar logger
logger = logging.getLogger('sysfree')

class ProformaService:
    """Servicio para gestionar proformas."""
    
    @classmethod
    @log_function_call
    @transaction.atomic
    def crear_proforma(cls, cliente, items, reparacion=None, direccion_facturacion=None, 
                      direccion_envio=None, notas="", validez=15, usuario=None):
        """
        Crea una nueva proforma.
        
        Args:
            cliente: Cliente para la proforma
            items: Lista de diccionarios con producto_id, cantidad, precio_unitario, descuento
            reparacion: Reparación asociada (opcional)
            direccion_facturacion: Dirección de facturación (opcional)
            direccion_envio: Dirección de envío (opcional)
            notas: Notas adicionales (opcional)
            validez: Días de validez de la proforma (opcional, por defecto 15)
            usuario: Usuario que crea la proforma
            
        Returns:
            Proforma: La proforma creada
        """
        # Generar número de proforma
        ultimo_numero = Proforma.objects.order_by('-numero').first()
        if ultimo_numero:
            try:
                num = int(ultimo_numero.numero.split('-')[1]) + 1
                numero = f"PRO-{num:06d}"
            except (ValueError, IndexError):
                numero = f"PRO-{timezone.now().strftime('%Y%m%d')}-001"
        else:
            numero = f"PRO-{timezone.now().strftime('%Y%m%d')}-001"
        
        # Crear proforma
        proforma = Proforma.objects.create(
            numero=numero,
            cliente=cliente,
            reparacion=reparacion,
            direccion_facturacion=direccion_facturacion,
            direccion_envio=direccion_envio,
            notas=notas,
            validez=validez,
            creado_por=usuario,
            modificado_por=usuario
        )
        
        # Agregar items
        subtotal = 0
        impuestos = 0
        
        for item in items:
            producto = Producto.objects.get(id=item['producto_id'])
            cantidad = item.get('cantidad', 1)
            precio_unitario = item.get('precio_unitario', producto.precio_venta)
            descuento = item.get('descuento', 0)
            
            # Calcular valores
            subtotal_item = cantidad * precio_unitario - descuento
            iva_item = subtotal_item * (producto.iva / 100)
            total_item = subtotal_item + iva_item
            
            # Crear detalle
            DetalleProforma.objects.create(
                proforma=proforma,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                descuento=descuento,
                iva=iva_item,
                subtotal=subtotal_item,
                total=total_item,
                creado_por=usuario,
                modificado_por=usuario
            )
            
            subtotal += subtotal_item
            impuestos += iva_item
        
        # Actualizar totales
        proforma.subtotal = subtotal
        proforma.iva = impuestos
        proforma.total = subtotal + impuestos
        proforma.save()
        
        logger.info(f"Proforma {proforma.numero} creada para cliente {cliente}")
        
        return proforma
    
    @classmethod
    @log_function_call
    @transaction.atomic
    def convertir_a_factura(cls, proforma, tipo='factura', usuario=None):
        """
        Convierte una proforma en factura.
        
        Args:
            proforma: Proforma a convertir
            tipo: Tipo de documento (factura, nota_venta, ticket)
            usuario: Usuario que realiza la conversión
            
        Returns:
            Venta: La factura creada
        """
        from ventas.services.venta_service import VentaService
        
        # Verificar que la proforma esté en estado aceptada
        if proforma.estado != 'aceptada':
            raise ValueError(_("Solo se pueden facturar proformas aceptadas"))
        
        # Preparar items para la venta
        items = []
        for detalle in proforma.detalles.all():
            items.append({
                'producto_id': detalle.producto.id,
                'cantidad': detalle.cantidad,
                'precio_unitario': detalle.precio_unitario,
                'descuento': detalle.descuento
            })
        
        # Crear venta
        venta = VentaService.crear_venta(
            cliente=proforma.cliente,
            tipo=tipo,
            items=items,
            direccion_facturacion=proforma.direccion_facturacion,
            direccion_envio=proforma.direccion_envio,
            notas=f"Generado desde proforma {proforma.numero}",
            usuario=usuario
        )
        
        # Actualizar proforma
        proforma.estado = 'facturada'
        proforma.factura = venta
        proforma.modificado_por = usuario
        proforma.save()
        
        logger.info(f"Proforma {proforma.numero} convertida a factura {venta.numero}")
        
        return venta