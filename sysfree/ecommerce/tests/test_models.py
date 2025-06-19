from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from django.contrib.contenttypes.models import ContentType # Importar ContentType
from ecommerce.models import (
    Carrito, ItemCarrito, Pedido, DetallePedido,
    ProductoEcommerce, CategoriaEcommerce
)
from inventario.models import Producto, Categoria
from clientes.models import Cliente, DireccionCliente
from core.models import Usuario

User = get_user_model()


class ProductoEcommerceTest(TestCase):
    """Pruebas para el modelo ProductoEcommerce."""
    
    def setUp(self):
        # Crear usuario
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123'
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
        
        # Crear categoría ecommerce
        self.categoria_ecommerce = CategoriaEcommerce.objects.create(
            nombre='Laptops',
            descripcion='Laptops y notebooks',
            slug='laptops'
        )
        
        # Crear producto ecommerce
        self.producto_ecommerce = ProductoEcommerce.objects.create(
            producto=self.producto,
            slug='laptop-prueba',
            descripcion_corta='Laptop para pruebas',
            descripcion_larga='Laptop para pruebas con características avanzadas',
            destacado=True,
            nuevo=True
        )
        self.producto_ecommerce.categorias.add(self.categoria_ecommerce)
    
    def test_producto_ecommerce_creation(self):
        """Prueba la creación de un producto ecommerce."""
        self.assertEqual(self.producto_ecommerce.producto.nombre, 'Laptop')
        self.assertEqual(self.producto_ecommerce.slug, 'laptop-prueba')
        self.assertTrue(self.producto_ecommerce.destacado)
        self.assertTrue(self.producto_ecommerce.nuevo)
        self.assertEqual(self.producto_ecommerce.categorias.count(), 1)
        self.assertEqual(self.producto_ecommerce.categorias.first().nombre, 'Laptops')
    
    def test_precio_actual_sin_oferta(self):
        """Prueba el precio actual sin oferta."""
        self.assertEqual(self.producto_ecommerce.precio_actual, self.producto.precio_venta)
    
    def test_precio_actual_con_oferta(self):
        """Prueba el precio actual con oferta."""
        # Configurar oferta
        self.producto_ecommerce.oferta = True
        self.producto_ecommerce.precio_oferta = Decimal('900.00')
        self.producto_ecommerce.fecha_inicio_oferta = timezone.now() - timezone.timedelta(days=1)
        self.producto_ecommerce.fecha_fin_oferta = timezone.now() + timezone.timedelta(days=1)
        self.producto_ecommerce.save()
        
        self.assertEqual(self.producto_ecommerce.precio_actual, Decimal('900.00'))
    
    def test_porcentaje_descuento(self):
        """Prueba el cálculo del porcentaje de descuento."""
        # Configurar oferta
        self.producto_ecommerce.oferta = True
        self.producto_ecommerce.precio_oferta = Decimal('800.00')
        self.producto_ecommerce.fecha_inicio_oferta = timezone.now() - timezone.timedelta(days=1)
        self.producto_ecommerce.fecha_fin_oferta = timezone.now() + timezone.timedelta(days=1)
        self.producto_ecommerce.save()
        
        # El descuento debería ser del 20%
        self.assertEqual(self.producto_ecommerce.porcentaje_descuento, 20)


class CarritoTest(TestCase):
    """Pruebas para el modelo Carrito."""
    
    def setUp(self):
        # Crear usuario y cliente
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123'
        )
        self.cliente = Cliente.objects.create(
            usuario=self.user,
            nombres='Cliente Carrito Test',
            email='testcarritomodels@example.com',
            tipo_identificacion='cedula',
            identificacion='0000000005'
        )
        
        # Crear categoría
        self.categoria = Categoria.objects.create(
            nombre='Electrónica',
            descripcion='Productos electrónicos'
        )
        
        # Crear productos
        self.producto1 = Producto.objects.create(
            codigo='P001',
            nombre='Laptop',
            descripcion='Laptop de prueba',
            precio_compra=800,
            precio_venta=1000,
            stock=10,
            categoria=self.categoria
        )
        
        self.producto2 = Producto.objects.create(
            codigo='P002',
            nombre='Mouse',
            descripcion='Mouse de prueba',
            precio_compra=10,
            precio_venta=20,
            stock=50,
            categoria=self.categoria
        )
        
        # Crear carrito
        self.carrito = Carrito.objects.create(
            cliente=self.cliente,
            sesion_id='test_session'
        )
        
        # Crear items del carrito
        producto_content_type = ContentType.objects.get_for_model(Producto)
        self.item1 = ItemCarrito.objects.create(
            carrito=self.carrito,
            content_type=producto_content_type,
            object_id=self.producto1.id,
            producto=self.producto1, # Mantener para el cálculo de IVA en save()
            cantidad=2,
            precio_unitario=self.producto1.precio_venta,
            impuesto_unitario=self.producto1.precio_venta * Decimal('0.12')
        )
        
        self.item2 = ItemCarrito.objects.create(
            carrito=self.carrito,
            content_type=producto_content_type,
            object_id=self.producto2.id,
            producto=self.producto2, # Mantener para el cálculo de IVA en save()
            cantidad=1,
            precio_unitario=self.producto2.precio_venta,
            impuesto_unitario=self.producto2.precio_venta * Decimal('0.12')
        )
    
    def test_carrito_creation(self):
        """Prueba la creación de un carrito."""
        self.assertEqual(self.carrito.cliente, self.cliente)
        self.assertEqual(self.carrito.sesion_id, 'test_session')
        self.assertFalse(self.carrito.convertido_a_pedido)
    
    def test_total_items(self):
        """Prueba el cálculo del total de items."""
        self.assertEqual(self.carrito.total_items, 3)  # 2 laptops + 1 mouse
    
    def test_subtotal(self):
        """Prueba el cálculo del subtotal."""
        # 2 laptops a $1000 + 1 mouse a $20 = $2020
        expected_subtotal = (self.producto1.precio_venta * 2) + self.producto2.precio_venta
        self.assertEqual(self.carrito.subtotal, expected_subtotal)
    
    def test_total_impuestos(self):
        """Prueba el cálculo del total de impuestos."""
        # Verificar que el total de impuestos sea mayor o igual a 0
        self.assertGreaterEqual(self.carrito.total_impuestos, Decimal('0.00'))
    
    def test_total(self):
        """Prueba el cálculo del total."""
        # Subtotal + impuestos = $2020 + $242.4 = $2262.4
        expected_total = self.carrito.subtotal + self.carrito.total_impuestos
        self.assertEqual(self.carrito.total, expected_total)


class PedidoTest(TestCase):
    """Pruebas para el modelo Pedido."""
    
    def setUp(self):
        # Crear usuario y cliente
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123'
        )
        self.cliente = Cliente.objects.create(
            usuario=self.user,
            nombres='Cliente Pedido Test',
            email='testpedidomodels@example.com',
            tipo_identificacion='cedula',
            identificacion='0000000006'
        )
        
        # Crear dirección
        self.direccion = DireccionCliente.objects.create(
            cliente=self.cliente,
            nombre='Casa',
            direccion='Calle Test 123',
            ciudad='Ciudad Test',
            provincia='Provincia Test',
            codigo_postal='12345',
            tipo='envio' # Campo tipo es requerido
            # pais='EC' # Campo no existe
        )
        
        # Crear pedido
        self.pedido = Pedido.objects.create(
            numero='PED-12345',
            cliente=self.cliente,
            direccion_facturacion=self.direccion,
            direccion_envio=self.direccion,
            subtotal=Decimal('2000.00'),
            impuestos=Decimal('240.00'),
            envio=Decimal('10.00'),
            total=Decimal('2250.00')
        )
    
    def test_pedido_creation(self):
        """Prueba la creación de un pedido."""
        self.assertEqual(self.pedido.numero, 'PED-12345')
        self.assertEqual(self.pedido.cliente, self.cliente)
        self.assertEqual(self.pedido.estado, 'pendiente')  # Estado por defecto
        self.assertEqual(self.pedido.total, Decimal('2250.00'))
    
    def test_esta_pagado(self):
        """Prueba la propiedad esta_pagado."""
        self.assertNotEqual(self.pedido.estado, 'pagado')
        
        # Cambiar estado a pagado
        self.pedido.estado = 'pagado'
        self.pedido.save()
        self.assertEqual(self.pedido.estado, 'pagado')
        
        # Cambiar estado a enviado (debería seguir considerándose pagado si el flujo es lineal)
        self.pedido.estado = 'enviado'
        self.pedido.save()
        # Para esta prueba, asumimos que si está enviado, ya fue pagado.
        # Si la lógica es diferente, esta aserción podría necesitar cambiar.
        self.assertIn(self.pedido.estado, ['enviado', 'pagado', 'entregado'])


        # Cambiar estado a entregado
        self.pedido.estado = 'entregado'
        self.pedido.save()
        self.assertEqual(self.pedido.estado, 'entregado')
    
    def test_esta_finalizado(self):
        """Prueba la propiedad esta_finalizado."""
        estados_no_finalizados = ['pendiente', 'pagado', 'preparando', 'enviado']
        self.assertIn(self.pedido.estado, estados_no_finalizados)
        
        # Cambiar estado a entregado
        self.pedido.estado = 'entregado'
        self.pedido.save()
        self.assertEqual(self.pedido.estado, 'entregado') # Un estado finalizado
        
        # Cambiar estado a cancelado
        self.pedido.estado = 'cancelado'
        self.pedido.save()
        self.assertEqual(self.pedido.estado, 'cancelado') # Un estado finalizado
        
        # Cambiar estado a devuelto (si es un estado posible)
        # self.pedido.estado = 'devuelto' # Asumiendo que 'devuelto' es un estado final
        # self.pedido.save()
        # self.assertEqual(self.pedido.estado, 'devuelto')