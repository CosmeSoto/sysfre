import logging
from django.utils import timezone
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache
from ventas.models import Venta, DetalleVenta
from inventario.models import Producto
from core.models import ConfiguracionSistema
from core.services import IVAService
from core.log_utils import log_function_call

logger = logging.getLogger('sysfree')

class VentaService:
    """Servicio para gestionar ventas, incluyendo proformas."""
    
    @classmethod
    def invalidar_cache_venta(cls, venta_id=None):
        """
        Invalida el caché relacionado con ventas.
        
        Args:
            venta_id (int, optional): ID de la venta específica a invalidar
        """
        # Invalidar caché general de ventas
        cache.delete('ventas_list')
        
        # Si se proporciona un ID de venta, invalidar caché específico
        if venta_id:
            try:
                # Obtener el cliente Redis
                from django_redis import get_redis_connection
                client = get_redis_connection("default")
                
                # Buscar claves que coincidan con el patrón
                for key in client.keys(f'*venta*{venta_id}*'):
                    client.delete(key)
                    
            except Exception as e:
                logger.error(f"Error al invalidar caché de venta: {str(e)}")
                # Si falla, al menos eliminamos la caché general
                pass
    
    @classmethod
    def generar_numero(cls, tipo):
        """Genera un número secuencial para el documento según su tipo."""
        try:
            config = ConfiguracionSistema.objects.first()
            if not config:
                config = ConfiguracionSistema.objects.create()
                
            if tipo == 'factura':
                prefijo = config.PREFIJO_FACTURA
                ultimo = Venta.objects.filter(tipo='factura').order_by('-numero').first()
                num = int(ultimo.numero[len(prefijo):]) + 1 if ultimo and ultimo.numero.startswith(prefijo) else config.INICIO_FACTURA
            elif tipo == 'proforma':
                prefijo = config.PREFIJO_PROFORMA
                ultimo = Venta.objects.filter(tipo='proforma').order_by('-numero').first()
                num = int(ultimo.numero[len(prefijo):]) + 1 if ultimo and ultimo.numero.startswith(prefijo) else config.INICIO_PROFORMA
            elif tipo == 'nota_venta':
                prefijo = config.PREFIJO_NOTA_VENTA
                ultimo = Venta.objects.filter(tipo='nota_venta').order_by('-numero').first()
                num = int(ultimo.numero[len(prefijo):]) + 1 if ultimo and ultimo.numero.startswith(prefijo) else config.INICIO_NOTA_VENTA
            elif tipo == 'ticket':
                prefijo = config.PREFIJO_TICKET
                ultimo = Venta.objects.filter(tipo='ticket').order_by('-numero').first()
                num = int(ultimo.numero[len(prefijo):]) + 1 if ultimo and ultimo.numero.startswith(prefijo) else config.INICIO_TICKET
            else:
                raise ValueError(f"Tipo de documento no válido: {tipo}")
                
            return f"{prefijo}{num:06d}"
            
        except Exception as e:
            logger.error(f"Error al generar número para {tipo}: {str(e)}")
            return f"{tipo.upper()}-{timezone.now().strftime('%Y%m%d')}-{timezone.now().strftime('%H%M%S')}"
    
    @classmethod
    @log_function_call
    @transaction.atomic
    def crear_venta(cls, cliente, tipo, items, direccion_facturacion=None, 
                   direccion_envio=None, notas="", reparacion=None, validez=15, usuario=None):
        """Crea una nueva venta o proforma."""
        numero = cls.generar_numero(tipo)
        
        venta = Venta.objects.create(
            numero=numero,
            cliente=cliente,
            tipo=tipo,
            estado='borrador' if tipo != 'proforma' else 'enviada',
            direccion_facturacion=direccion_facturacion,
            direccion_envio=direccion_envio,
            notas=notas,
            reparacion=reparacion,
            validez=validez if tipo == 'proforma' else 0,
            creado_por=usuario,
            modificado_por=usuario
        )
        
        subtotal = 0
        descuento = 0
        
        for item in items:
            producto = Producto.objects.get(id=item['producto_id'])
            cantidad = item.get('cantidad', 1)
            precio_unitario = item.get('precio_unitario', producto.precio_venta)
            item_descuento = item.get('descuento', 0)
            
            subtotal_item = cantidad * precio_unitario - item_descuento
            
            # Usar el servicio IVA para calcular el IVA
            tipo_iva = item.get('tipo_iva') or producto.tipo_iva or IVAService.get_default()
            iva_item, total_item = IVAService.calcular_iva(subtotal_item, tipo_iva)
            
            DetalleVenta.objects.create(
                venta=venta,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                descuento=item_descuento,
                tipo_iva=tipo_iva,
                iva=iva_item,
                subtotal=subtotal_item,
                total=total_item,
                creado_por=usuario,
                modificado_por=usuario
            )
            
            subtotal += subtotal_item
            descuento += item_descuento
        
        venta.subtotal = subtotal
        venta.descuento = descuento
        venta.total = sum(detalle.total for detalle in venta.detalles.all())
        venta.save()
        
        # Invalidar caché
        cls.invalidar_cache_venta()
        
        logger.info(f"{tipo.capitalize()} {venta.numero} creada para cliente {cliente}")
        
        return venta
    
    @classmethod
    @log_function_call
    @transaction.atomic
    def convertir_proforma_a_factura(cls, proforma, usuario=None):
        """Convierte una proforma (Venta con tipo='proforma') en factura."""
        if proforma.tipo != 'proforma':
            raise ValueError(_("Solo se pueden convertir proformas a facturas"))
        if proforma.esta_vencida:
            raise ValueError(_("No se puede convertir una proforma vencida"))
        if proforma.estado != 'aceptada':
            raise ValueError(_("Solo se pueden facturar proformas aceptadas"))
        
        items = []
        for detalle in proforma.detalles.all():
            items.append({
                'producto_id': detalle.producto.id,
                'cantidad': detalle.cantidad,
                'precio_unitario': detalle.precio_unitario,
                'descuento': detalle.descuento,
                'tipo_iva': detalle.tipo_iva
            })
        
        factura = cls.crear_venta(
            cliente=proforma.cliente,
            tipo='factura',
            items=items,
            direccion_facturacion=proforma.direccion_facturacion,
            direccion_envio=proforma.direccion_envio,
            notas=f"Generado desde proforma {proforma.numero}",
            reparacion=proforma.reparacion,
            usuario=usuario
        )
        
        proforma.estado = 'facturada'
        proforma.venta_relacionada = factura
        proforma.modificado_por = usuario
        proforma.save()
        
        factura.venta_relacionada = proforma
        factura.save()
        
        # Invalidar caché
        cls.invalidar_cache_venta()
        cls.invalidar_cache_venta(proforma.id)
        cls.invalidar_cache_venta(factura.id)
        
        logger.info(f"Proforma {proforma.numero} convertida a factura {factura.numero}")
        
        return factura