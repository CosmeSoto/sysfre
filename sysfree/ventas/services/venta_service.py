import logging
from django.utils import timezone
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from ventas.models import Venta, DetalleVenta
from inventario.models import Producto
from core.models import ConfiguracionSistema
from core.log_utils import log_function_call

# Configurar logger
logger = logging.getLogger('sysfree')

class VentaService:
    """Servicio para gestionar ventas."""
    
    @classmethod
    def generar_numero(cls, tipo):
        """
        Genera un número secuencial para el documento según su tipo.
        
        Args:
            tipo: Tipo de documento (factura, proforma, nota_venta, ticket)
            
        Returns:
            str: Número generado
        """
        try:
            config = ConfiguracionSistema.objects.first()
            if not config:
                config = ConfiguracionSistema.objects.create()
                
            if tipo == 'factura':
                prefijo = config.PREFIJO_FACTURA
                ultimo = Venta.objects.filter(tipo='factura').order_by('-numero').first()
                if ultimo and ultimo.numero.startswith(prefijo):
                    try:
                        num = int(ultimo.numero[len(prefijo):]) + 1
                    except ValueError:
                        num = config.INICIO_FACTURA
                else:
                    num = config.INICIO_FACTURA
                    
            elif tipo == 'proforma':
                prefijo = config.PREFIJO_PROFORMA
                ultimo = Venta.objects.filter(tipo='proforma').order_by('-numero').first()
                if ultimo and ultimo.numero.startswith(prefijo):
                    try:
                        num = int(ultimo.numero[len(prefijo):]) + 1
                    except ValueError:
                        num = config.INICIO_PROFORMA
                else:
                    num = config.INICIO_PROFORMA
                    
            elif tipo == 'nota_venta':
                prefijo = config.PREFIJO_NOTA_VENTA
                ultimo = Venta.objects.filter(tipo='nota_venta').order_by('-numero').first()
                if ultimo and ultimo.numero.startswith(prefijo):
                    try:
                        num = int(ultimo.numero[len(prefijo):]) + 1
                    except ValueError:
                        num = config.INICIO_NOTA_VENTA
                else:
                    num = config.INICIO_NOTA_VENTA
                    
            elif tipo == 'ticket':
                prefijo = config.PREFIJO_TICKET
                ultimo = Venta.objects.filter(tipo='ticket').order_by('-numero').first()
                if ultimo and ultimo.numero.startswith(prefijo):
                    try:
                        num = int(ultimo.numero[len(prefijo):]) + 1
                    except ValueError:
                        num = config.INICIO_TICKET
                else:
                    num = config.INICIO_TICKET
            else:
                raise ValueError(f"Tipo de documento no válido: {tipo}")
                
            return f"{prefijo}{num:06d}"
            
        except Exception as e:
            logger.error(f"Error al generar número para {tipo}: {str(e)}")
            # Fallback en caso de error
            return f"{tipo.upper()}-{timezone.now().strftime('%Y%m%d')}-{timezone.now().strftime('%H%M%S')}"
    
    @classmethod
    @log_function_call
    @transaction.atomic
    def crear_venta(cls, cliente, tipo, items, direccion_facturacion=None, 
                   direccion_envio=None, notas="", reparacion=None, validez=15, usuario=None):
        """
        Crea una nueva venta.
        
        Args:
            cliente: Cliente para la venta
            tipo: Tipo de documento (factura, proforma, nota_venta, ticket)
            items: Lista de diccionarios con producto_id, cantidad, precio_unitario, descuento
            direccion_facturacion: Dirección de facturación (opcional)
            direccion_envio: Dirección de envío (opcional)
            notas: Notas adicionales (opcional)
            reparacion: Reparación asociada (opcional)
            validez: Días de validez (solo para proformas)
            usuario: Usuario que crea la venta
            
        Returns:
            Venta: La venta creada
        """
        # Generar número de venta
        numero = cls.generar_numero(tipo)
        
        # Crear venta
        venta = Venta.objects.create(
            numero=numero,
            cliente=cliente,
            tipo=tipo,
            direccion_facturacion=direccion_facturacion,
            direccion_envio=direccion_envio,
            notas=notas,
            reparacion=reparacion,
            validez=validez if tipo == 'proforma' else 0,
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
            DetalleVenta.objects.create(
                venta=venta,
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
        venta.subtotal = subtotal
        venta.iva = impuestos
        venta.total = subtotal + impuestos
        venta.save()
        
        logger.info(f"{tipo.capitalize()} {venta.numero} creada para cliente {cliente}")
        
        return venta
    
    @classmethod
    @log_function_call
    @transaction.atomic
    def convertir_proforma_a_factura(cls, proforma, usuario=None):
        """
        Convierte una proforma en factura.
        
        Args:
            proforma: Proforma a convertir
            usuario: Usuario que realiza la conversión
            
        Returns:
            Venta: La factura creada
        """
        # Verificar que sea una proforma
        if proforma.tipo != 'proforma':
            raise ValueError(_("Solo se pueden convertir proformas a facturas"))
        
        # Verificar que no esté vencida
        if proforma.esta_vencida:
            raise ValueError(_("No se puede convertir una proforma vencida"))
        
        # Preparar items para la factura
        items = []
        for detalle in proforma.detalles.all():
            items.append({
                'producto_id': detalle.producto.id,
                'cantidad': detalle.cantidad,
                'precio_unitario': detalle.precio_unitario,
                'descuento': detalle.descuento
            })
        
        # Crear factura
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
        
        # Actualizar proforma
        proforma.estado = 'emitida'
        proforma.venta_relacionada = factura
        proforma.modificado_por = usuario
        proforma.save()
        
        # Actualizar factura
        factura.venta_relacionada = proforma
        factura.save()
        
        logger.info(f"Proforma {proforma.numero} convertida a factura {factura.numero}")
        
        return factura