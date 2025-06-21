import logging
from django.utils import timezone
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from ventas.models import Venta, DetalleVenta
from inventario.models import Producto
from core.models import ConfiguracionSistema
from core.services import IVAService
from core.services.cache_service import CacheService
from core.services.auditoria_service import AuditoriaService
from core.log_utils import log_function_call
from inventario.services import InventarioService

logger = logging.getLogger('sysfree')

class VentaService:
    """Servicio para gestionar ventas, incluyendo proformas."""
    
    @classmethod
    def invalidar_cache_venta(cls, venta_id=None):
        """Invalida el caché relacionado con ventas."""
        try:
            CacheService.delete('ventas_list')
            if venta_id:
                CacheService.delete_pattern(f'*venta*{venta_id}*')
        except Exception as e:
            logger.error(f"Error al invalidar caché de venta: {str(e)}")
    
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
        
        detalles_a_crear = []
        productos_a_actualizar = []
        
        tipo_iva_default = IVAService.get_default()

        for item in items:
            try:
                producto = Producto.objects.select_related('tipo_iva').get(id=item['producto_id'])
            except Producto.DoesNotExist:
                raise ValueError(f"Producto con id {item['producto_id']} no encontrado.")

            cantidad = item.get('cantidad', 1)
            precio_unitario = item.get('precio_unitario', producto.precio_venta)
            item_descuento = item.get('descuento', 0)
            
            if producto.es_inventariable and producto.stock < cantidad:
                raise ValueError(f"Stock insuficiente para el producto {producto.nombre}.")

            subtotal_item = cantidad * precio_unitario - item_descuento
            
            tipo_iva = item.get('tipo_iva') or producto.tipo_iva or tipo_iva_default
            iva_item, total_item = IVAService.calcular_iva(subtotal_item, tipo_iva)
            
            detalles_a_crear.append(
                DetalleVenta(
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
            )
            
            if producto.es_inventariable:
                productos_a_actualizar.append({'producto': producto, 'cantidad': cantidad})

        DetalleVenta.objects.bulk_create(detalles_a_crear)
        
        # Actualizar stock y totales
        venta.actualizar_totales()
        
        for item_actualizar in productos_a_actualizar:
            InventarioService.registrar_salida(
                producto=item_actualizar['producto'],
                cantidad=item_actualizar['cantidad'],
                origen='venta',
                documento=venta.numero,
                usuario=usuario,
                referencia_id=venta.id,
                referencia_tipo='Venta'
            )
        
        # Registrar auditoría
        AuditoriaService.venta_creada(venta, detalles_a_crear)
        
        # Invalidar caché
        cls.invalidar_cache_venta()
        
        logger.info(f"{tipo.capitalize()} {venta.numero} creada para cliente {cliente}")
        
        return venta
    
    @classmethod
    @log_function_call
    @transaction.atomic
    def cambiar_estado_venta(cls, venta, nuevo_estado, usuario=None):
        """Cambia el estado de una venta."""
        estados_validos = ['borrador', 'pendiente', 'pagada', 'enviada', 'entregada', 'cancelada']
        if nuevo_estado not in estados_validos:
            raise ValueError(_(f"Estado no válido. Debe ser uno de: {', '.join(estados_validos)}"))
        
        venta.estado = nuevo_estado
        venta.modificado_por = usuario
        venta.save()
        
        # Registrar auditoría
        AuditoriaService.registrar_actividad_personalizada(
            accion="CAMBIO_ESTADO_VENTA",
            descripcion=f"Venta {venta.numero} cambió a estado {nuevo_estado}",
            modelo="Venta",
            objeto_id=venta.id,
            datos={'estado_anterior': venta.estado, 'estado_nuevo': nuevo_estado}
        )
        
        # Invalidar caché
        cls.invalidar_cache_venta(venta.id)
        
        logger.info(f"Venta {venta.numero} actualizada a estado {nuevo_estado}")
        
        return venta
    
    @classmethod
    @log_function_call
    @transaction.atomic
    def registrar_pago(cls, venta, metodo, monto, referencia='', datos_adicionales=None, usuario=None):
        """Registra un pago para una venta."""
        from ventas.models import Pago
        
        if venta.estado == 'cancelada':
            raise ValueError(_("No se puede registrar un pago para una venta cancelada"))
        
        pago = Pago.objects.create(
            venta=venta,
            metodo=metodo,
            monto=monto,
            referencia=referencia,
            estado='completado',
            creado_por=usuario,
            modificado_por=usuario
        )
        
        # Actualizar estado de la venta si el pago cubre el total
        from django.db.models import Sum
        total_pagado = Pago.objects.filter(venta=venta, estado='completado').aggregate(
            total=Sum('monto')
        )['total'] or 0
        
        if total_pagado >= venta.total:
            venta.estado = 'pagada'
            venta.modificado_por = usuario
            venta.save()
        
        # Registrar auditoría
        AuditoriaService.registrar_actividad_personalizada(
            accion="PAGO_REGISTRADO",
            descripcion=f"Pago registrado para venta {venta.numero}: {metodo} - ${monto}",
            modelo="Pago",
            objeto_id=pago.id,
            datos={'venta': venta.numero, 'metodo': metodo, 'monto': str(monto)}
        )
        
        # Invalidar caché
        cls.invalidar_cache_venta(venta.id)
        
        logger.info(f"Pago registrado para venta {venta.numero}: {metodo} - {monto}")
        
        return pago
    
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