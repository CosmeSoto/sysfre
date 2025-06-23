from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from ..models import Carrito, ItemCarrito
from inventario.models import Producto
from reparaciones.models import ServicioReparacion
from core.services.cache_service import CacheService
from core.services.auditoria_service import AuditoriaService
import logging

logger = logging.getLogger('sysfree')


class CarritoService:
    """Servicio para gestionar el carrito de compras."""
    
    @classmethod
    def invalidar_cache_carrito(cls, carrito_id=None, cliente_id=None):
        """Invalida el caché relacionado con carritos."""
        try:
            if carrito_id:
                CacheService.delete_pattern(f'*carrito*{carrito_id}*')
            if cliente_id:
                CacheService.delete_pattern(f'*carrito*cliente*{cliente_id}*')
        except Exception as e:
            logger.error(f"Error al invalidar caché de carrito: {str(e)}")
    
    @staticmethod
    def obtener_o_crear_carrito(request):
        """
        Obtiene el carrito actual o crea uno nuevo.
        
        Args:
            request: Objeto request de Django
            
        Returns:
            Objeto Carrito
        """
        if request.user.is_authenticated:
            # Usuario autenticado: buscar por usuario
            carrito, creado = Carrito.objects.get_or_create(
                cliente=request.user.cliente,
                convertido_a_pedido=False,
                defaults={'sesion_id': request.session.session_key}
            )
        else:
            # Usuario anónimo: buscar por sesión
            if not request.session.session_key:
                request.session.save()
                
            carrito, creado = Carrito.objects.get_or_create(
                sesion_id=request.session.session_key,
                convertido_a_pedido=False
            )
        
        return carrito
    
    @staticmethod
    @transaction.atomic
    def agregar_item(carrito, item_id, cantidad=1, es_servicio=False):
        """
        Agrega un item al carrito.
        
        Args:
            carrito: Objeto Carrito
            item_id: ID del producto o servicio
            cantidad: Cantidad a agregar
            es_servicio: Indica si es un servicio o un producto
            
        Returns:
            Objeto ItemCarrito
        """
        try:
            cantidad = int(cantidad)
            if cantidad <= 0:
                raise ValueError(_("La cantidad debe ser mayor que cero"))
                
            if es_servicio:
                # Es un servicio
                servicio = ServicioReparacion.objects.get(id=item_id)
                
                # Verificar si el servicio está disponible online
                if not servicio.disponible_online:
                    raise ValueError(_("Este servicio no está disponible para compra online"))
                
                # Obtener el ContentType para ServicioReparacion
                content_type = ContentType.objects.get_for_model(ServicioReparacion)
                
                # Buscar si ya existe en el carrito
                item, creado = ItemCarrito.objects.get_or_create(
                    carrito=carrito,
                    content_type=content_type,
                    object_id=servicio.id,
                    defaults={
                        'es_servicio': True,
                        'cantidad': cantidad,
                        'precio_unitario': servicio.precio
                    }
                )
                
                if not creado:
                    # Si ya existe, actualizar la cantidad
                    item.cantidad += cantidad
                    item.save()
                
                # Actualizar totales del carrito
                carrito.actualizar_totales()
                
                logger.info(f"Servicio {servicio.nombre} agregado al carrito {carrito.id}")
                
                # Registrar auditoría
                AuditoriaService.registrar_actividad_personalizada(
                    accion="SERVICIO_AGREGADO_CARRITO",
                    descripcion=f"Servicio agregado al carrito: {servicio.nombre} x{cantidad}",
                    modelo="ItemCarrito",
                    objeto_id=item.id,
                    datos={'servicio': servicio.nombre, 'cantidad': cantidad, 'precio': str(servicio.precio)}
                )
                
                # Invalidar caché
                CarritoService.invalidar_cache_carrito(carrito.id)
                if carrito.cliente:
                    CarritoService.invalidar_cache_carrito(cliente_id=carrito.cliente.id)
                
            else:
                # Es un producto
                producto = Producto.objects.get(id=item_id)
                
                # Verificar si el producto está disponible
                if not producto.disponible:
                    raise ValueError(_("Este producto no está disponible"))
                
                # Verificar stock si es inventariable
                if producto.es_inventariable and producto.stock < cantidad:
                    raise ValueError(_("No hay suficiente stock disponible"))
                
                # Obtener el ContentType para Producto
                content_type = ContentType.objects.get_for_model(Producto)
                
                # Buscar si ya existe en el carrito
                item, creado = ItemCarrito.objects.get_or_create(
                    carrito=carrito,
                    content_type=content_type,
                    object_id=producto.id,
                    defaults={
                        'producto': producto,
                        'es_servicio': False,
                        'cantidad': cantidad,
                        'precio_unitario': producto.precio_venta
                    }
                )
                
                if not creado:
                    # Si ya existe, actualizar la cantidad
                    item.cantidad += cantidad
                    item.save()
                
                # Actualizar totales del carrito
                carrito.actualizar_totales()
                
                logger.info(f"Producto {producto.nombre} agregado al carrito {carrito.id}")
                
                # Registrar auditoría
                AuditoriaService.registrar_actividad_personalizada(
                    accion="PRODUCTO_AGREGADO_CARRITO",
                    descripcion=f"Producto agregado al carrito: {producto.nombre} x{cantidad}",
                    modelo="ItemCarrito",
                    objeto_id=item.id,
                    datos={'producto': producto.nombre, 'cantidad': cantidad, 'precio': str(producto.precio_venta)}
                )
                
                # Invalidar caché
                CarritoService.invalidar_cache_carrito(carrito.id)
                if carrito.cliente:
                    CarritoService.invalidar_cache_carrito(cliente_id=carrito.cliente.id)
            
            return item
            
        except (Producto.DoesNotExist, ServicioReparacion.DoesNotExist):
            raise ValueError(_("El producto o servicio no existe"))
        except Exception as e:
            logger.error(f"Error al agregar item al carrito: {str(e)}")
            raise
    
    @staticmethod
    def actualizar_item(carrito, item_id, cantidad):
        """
        Actualiza la cantidad de un item en el carrito.
        
        Args:
            carrito: Objeto Carrito
            item_id: ID del ItemCarrito
            cantidad: Nueva cantidad
            
        Returns:
            Objeto ItemCarrito actualizado
        """
        try:
            cantidad = int(cantidad)
            if cantidad <= 0:
                return CarritoService.eliminar_item(carrito, item_id)
                
            item = ItemCarrito.objects.get(id=item_id, carrito=carrito)
            
            # Verificar stock si es un producto inventariable
            if not item.es_servicio and item.producto.es_inventariable and item.producto.stock < cantidad:
                raise ValueError(_("No hay suficiente stock disponible"))
                
            item.cantidad = cantidad
            item.save()
            
            # Actualizar totales del carrito
            carrito.actualizar_totales()
            
            # Invalidar caché
            CarritoService.invalidar_cache_carrito(carrito.id)
            if carrito.cliente:
                CarritoService.invalidar_cache_carrito(cliente_id=carrito.cliente.id)
            
            logger.info(f"Item {item_id} actualizado en carrito {carrito.id}")
            return item
            
        except ItemCarrito.DoesNotExist:
            raise ValueError(_("El item no existe en el carrito"))
        except Exception as e:
            logger.error(f"Error al actualizar item en carrito: {str(e)}")
            raise
    
    @staticmethod
    def eliminar_item(carrito, item_id):
        """
        Elimina un item del carrito.
        
        Args:
            carrito: Objeto Carrito
            item_id: ID del ItemCarrito
            
        Returns:
            True si se eliminó correctamente
        """
        try:
            item = ItemCarrito.objects.get(id=item_id, carrito=carrito)
            item.delete()
            
            # Actualizar totales del carrito
            carrito.actualizar_totales()
            
            # Invalidar caché
            CarritoService.invalidar_cache_carrito(carrito.id)
            if carrito.cliente:
                CarritoService.invalidar_cache_carrito(cliente_id=carrito.cliente.id)
            
            logger.info(f"Item {item_id} eliminado del carrito {carrito.id}")
            return True
            
        except ItemCarrito.DoesNotExist:
            raise ValueError(_("El item no existe en el carrito"))
        except Exception as e:
            logger.error(f"Error al eliminar item del carrito: {str(e)}")
            raise
    
    @staticmethod
    def vaciar_carrito(carrito):
        """
        Elimina todos los items del carrito.
        
        Args:
            carrito: Objeto Carrito
            
        Returns:
            True si se vació correctamente
        """
        try:
            carrito.items.all().delete()
            
            # Actualizar totales del carrito
            carrito._subtotal = 0
            carrito._total_impuestos = 0
            carrito._total = 0
            carrito.save(update_fields=['_subtotal', '_total_impuestos', '_total'])
            
            # Invalidar caché
            CarritoService.invalidar_cache_carrito(carrito.id)
            if carrito.cliente:
                CarritoService.invalidar_cache_carrito(cliente_id=carrito.cliente.id)
            
            logger.info(f"Carrito {carrito.id} vaciado")
            return True
            
        except Exception as e:
            logger.error(f"Error al vaciar carrito: {str(e)}")
            raise