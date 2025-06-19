from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from ecommerce.models import (
    Carrito, ItemCarrito, Pedido, DetallePedido
)
from ecommerce.services.carrito_service import CarritoService
from ecommerce.services.pedido_service import PedidoService
from inventario.models import Producto, Categoria
from clientes.models import Cliente, DireccionCliente
from reparaciones.models import ServicioReparacion, Reparacion
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


class CarritoServiceTest(TestCase):
    """Pruebas para el servicio CarritoService."""
    
    def setUp(self):
        # Crear usuario y cliente
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123'
        )
        self.cliente = Cliente.objects.create(
            usuario=self.user,
            nombres='Cliente Test Carrito',
            email='testcarrito@example.com',
            tipo_identificacion='cedula',
            identificacion='0000000001'
        )
        
        # Crear categoría
        self.categoria = Categoria.objects.create(
            nombre='Electrónica',
            descripcion='Productos electrónicos'
        )
        
        # Crear producto
        self.producto = Producto.objects.create(
            codigo='P001',
            nombre='Laptop',
            descripcion='Laptop de prueba',
            precio_compra=800,
            precio_venta=1000,
            stock=10,
            categoria=self.categoria
        )
        
        # Crear servicio
        self.servicio = ServicioReparacion.objects.create(
            nombre='Reparación de laptop',
            descripcion='Servicio de reparación de laptop',
            tipo='reparacion',
            precio=150,
            tiempo_estimado=2,
            producto=Producto.objects.create(
                codigo='S001',
                nombre='Servicio de reparación',
                descripcion='Servicio de reparación',
                precio_compra=0,
                precio_venta=150,
                stock=0,
                categoria=self.categoria,
                es_inventariable=False,
                tipo='servicio'
            ),
            disponible_online=True
        )
        
        # Crear carrito
        self.carrito = Carrito.objects.create(
            cliente=self.cliente,
            sesion_id='test_session'
        )
    
    def test_agregar_producto(self):
        """Prueba agregar un producto al carrito."""
        item = CarritoService.agregar_item(self.carrito, self.producto.id, 2, False)
        
        self.assertEqual(item.carrito, self.carrito)
        self.assertEqual(item.producto, self.producto)
        self.assertEqual(item.cantidad, 2)
        self.assertEqual(item.precio_unitario, self.producto.precio_venta)
        self.assertGreaterEqual(item.impuesto_unitario, Decimal('0.00'))
        self.assertFalse(item.es_servicio)
    
    def test_agregar_servicio(self):
        """Prueba agregar un servicio al carrito."""
        item = CarritoService.agregar_item(self.carrito, self.servicio.id, 1, True)
        
        self.assertEqual(item.carrito, self.carrito)
        self.assertEqual(item.item, self.servicio)
        self.assertEqual(item.cantidad, 1)
        self.assertEqual(item.precio_unitario, self.servicio.precio)
        self.assertTrue(item.es_servicio)
    
    def test_actualizar_item(self):
        """Prueba actualizar la cantidad de un item en el carrito."""
        # Agregar item
        item = CarritoService.agregar_item(self.carrito, self.producto.id, 1, False)
        
        # Actualizar cantidad
        updated_item = CarritoService.actualizar_item(self.carrito, item.id, 3)
        
        self.assertEqual(updated_item.cantidad, 3)
    
    def test_eliminar_item(self):
        """Prueba eliminar un item del carrito."""
        # Agregar item
        item = CarritoService.agregar_item(self.carrito, self.producto.id, 1, False)
        
        # Verificar que existe
        self.assertTrue(ItemCarrito.objects.filter(id=item.id).exists())
        
        # Eliminar item
        result = CarritoService.eliminar_item(self.carrito, item.id)
        
        # Verificar que se eliminó
        self.assertTrue(result)
        self.assertFalse(ItemCarrito.objects.filter(id=item.id).exists())
    
    def test_vaciar_carrito(self):
        """Prueba vaciar el carrito."""
        # Agregar items
        CarritoService.agregar_item(self.carrito, self.producto.id, 1, False)
        CarritoService.agregar_item(self.carrito, self.servicio.id, 1, True)
        
        # Verificar que existen items
        self.assertEqual(self.carrito.items.count(), 2)
        
        # Vaciar carrito
        result = CarritoService.vaciar_carrito(self.carrito)
        
        # Verificar que se vació
        self.assertTrue(result)
        self.assertEqual(self.carrito.items.count(), 0)


class PedidoServiceTest(TestCase):
    """Pruebas para el servicio PedidoService."""
    
    def setUp(self):
        # Crear usuario y cliente
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123'
        )
        self.cliente = Cliente.objects.create(
            usuario=self.user,
            nombres='Cliente Test Pedido',
            email='testpedido@example.com',
            tipo_identificacion='cedula',
            identificacion='0000000002'
        )
        
        # Crear dirección
        self.direccion = DireccionCliente.objects.create(
            cliente=self.cliente,
            tipo='envio', # Campo tipo es requerido
            nombre='Casa',
            direccion='Calle Test 123',
            ciudad='Ciudad Test',
            provincia='Provincia Test',
            codigo_postal='12345'
            # pais='EC' # Campo no existe
        )
        
        # Crear categoría
        self.categoria = Categoria.objects.create(
            nombre='Electrónica',
            descripcion='Productos electrónicos'
        )
        
        # Crear producto
        self.producto = Producto.objects.create(
            codigo='P001',
            nombre='Laptop',
            descripcion='Laptop de prueba',
            precio_compra=800,
            precio_venta=1000,
            stock=10,
            categoria=self.categoria
        )
        
        # Crear servicio
        self.servicio = ServicioReparacion.objects.create(
            nombre='Reparación de laptop',
            descripcion='Servicio de reparación de laptop',
            tipo='reparacion',
            precio=150,
            tiempo_estimado=2,
            producto=Producto.objects.create(
                codigo='S001',
                nombre='Servicio de reparación',
                descripcion='Servicio de reparación',
                precio_compra=0,
                precio_venta=150,
                stock=0,
                categoria=self.categoria,
                es_inventariable=False,
                tipo='servicio'
            ),
            disponible_online=True
        )
        
        # Crear carrito
        self.carrito = Carrito.objects.create(
            cliente=self.cliente,
            sesion_id='test_session'
        )
        
        # Agregar items al carrito
        self.producto_ct = ContentType.objects.get_for_model(Producto)
        self.servicio_ct = ContentType.objects.get_for_model(ServicioReparacion)
        
        # Item producto
        self.item_producto = ItemCarrito.objects.create(
            carrito=self.carrito,
            content_type=self.producto_ct,
            object_id=self.producto.id,
            producto=self.producto,
            es_servicio=False,
            cantidad=2,
            precio_unitario=self.producto.precio_venta,
            impuesto_unitario=self.producto.precio_venta * Decimal('0.12')
        )
        
        # Item servicio
        self.item_servicio = ItemCarrito.objects.create(
            carrito=self.carrito,
            content_type=self.servicio_ct,
            object_id=self.servicio.id,
            es_servicio=True,
            cantidad=1,
            precio_unitario=self.servicio.precio,
            impuesto_unitario=self.servicio.precio * Decimal('0.12')
        )
    
    def test_crear_pedido_desde_carrito(self):
        """Prueba crear un pedido desde un carrito."""
        # Crear pedido
        pedido = PedidoService.crear_pedido_desde_carrito(
            carrito=self.carrito,
            direccion_facturacion=self.direccion,
            direccion_envio=self.direccion,
            notas='Notas de prueba'
        )
        
        # Verificar pedido
        self.assertEqual(pedido.cliente, self.cliente)
        self.assertEqual(pedido.direccion_facturacion, self.direccion)
        self.assertEqual(pedido.direccion_envio, self.direccion)
        self.assertEqual(pedido.notas, 'Notas de prueba')
        self.assertEqual(pedido.estado, 'pendiente')
        
        # Verificar detalles
        self.assertEqual(pedido.detalles.count(), 2)
        
        # Verificar que el carrito está marcado como convertido
        self.carrito.refresh_from_db()
        self.assertTrue(self.carrito.convertido_a_pedido)
        
        # Verificar que se creó un ticket de reparación para el servicio
        detalle_servicio = pedido.detalles.get(es_servicio=True)
        self.assertIsNotNone(detalle_servicio.reparacion)
        self.assertEqual(detalle_servicio.reparacion.cliente, self.cliente)
        self.assertEqual(detalle_servicio.reparacion.problema_reportado, f"Servicio solicitado: {self.servicio.nombre}")
    
    def test_actualizar_estado_pedido(self):
        """Prueba actualizar el estado de un pedido."""
        # Crear pedido
        pedido = Pedido.objects.create(
            numero='PED-12345',
            cliente=self.cliente,
            direccion_facturacion=self.direccion,
            direccion_envio=self.direccion,
            subtotal=Decimal('2000.00'),
            impuestos=Decimal('240.00'),
            total=Decimal('2240.00')
        )
        
        # Actualizar a pagado
        updated_pedido = PedidoService.actualizar_estado_pedido(pedido, 'pagado')
        self.assertEqual(updated_pedido.estado, 'pagado')
        self.assertIsNotNone(updated_pedido.fecha_pago)
        
        # Actualizar a enviado
        updated_pedido = PedidoService.actualizar_estado_pedido(pedido, 'enviado')
        self.assertEqual(updated_pedido.estado, 'enviado')
        self.assertIsNotNone(updated_pedido.fecha_envio)
        
        # Actualizar a entregado
        updated_pedido = PedidoService.actualizar_estado_pedido(pedido, 'entregado')
        self.assertEqual(updated_pedido.estado, 'entregado')
        self.assertIsNotNone(updated_pedido.fecha_entrega)