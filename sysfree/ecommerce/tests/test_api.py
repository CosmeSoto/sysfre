from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from ecommerce.models import (
    CategoriaEcommerce, ProductoEcommerce, Carrito, ItemCarrito,
    Pedido, DetallePedido, PagoOnline
)
from clientes.models import Cliente, DireccionCliente
from inventario.models import Producto, Categoria

User = get_user_model()


class EcommerceAPITests(TestCase):
    """Pruebas para la API de ecommerce."""
    
    def setUp(self):
        """Configuración inicial para las pruebas."""
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            nombres='Test User'
        )
        
        # Crear usuario administrador
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='adminpass123',
            nombres='Admin User',
            is_staff=True,
            is_superuser=True
        )
        
        # Crear cliente de prueba
        self.cliente = Cliente.objects.create(
            tipo_identificacion='cedula',
            identificacion='1234567890',
            nombres='Cliente',
            apellidos='Prueba',
            email='cliente@example.com',
            telefono='0987654321',
            usuario=self.user
        )
        
        # Crear dirección de prueba
        self.direccion = DireccionCliente.objects.create(
            cliente=self.cliente,
            tipo='facturacion',
            direccion='Calle Principal 123',
            ciudad='Ciudad Prueba',
            provincia='Provincia Prueba',
            es_principal=True
        )
        
        # Crear categoría de inventario
        self.categoria_inv = Categoria.objects.create(
            nombre='Categoría de prueba',
            descripcion='Descripción de prueba'
        )
        
        # Crear producto de inventario
        self.producto_inv = Producto.objects.create(
            codigo='P001',
            nombre='Producto de prueba',
            descripcion='Descripción de prueba',
            precio_compra=100,
            precio_venta=150,
            stock=10,
            categoria=self.categoria_inv
        )
        
        # Crear categoría de ecommerce
        self.categoria = CategoriaEcommerce.objects.create(
            nombre='Categoría Ecommerce',
            slug='categoria-ecommerce',
            descripcion='Descripción de prueba',
            mostrar_en_menu=True,
            activo=True
        )
        
        # Crear producto de ecommerce
        self.producto = ProductoEcommerce.objects.create(
            producto=self.producto_inv,
            slug='producto-prueba',
            descripcion_corta='Descripción corta',
            descripcion_larga='Descripción larga',
            destacado=True,
            nuevo=True,
            oferta=False,
            precio_oferta=0,
            activo=True
        )
        self.producto.categorias.add(self.categoria)
        
        # Crear carrito de prueba
        self.carrito = Carrito.objects.create(
            cliente=self.cliente,
            sesion_id='test_session',
            _subtotal=150,
            _total=150
        )
        
        # Cliente API
        self.client = APIClient()
    
    def test_login_required(self):
        """Prueba que se requiera autenticación para acceder a la API."""
        response = self.client.get(reverse('api:pedido-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_authenticated_user_can_access(self):
        """Prueba que un usuario autenticado pueda acceder a la API."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('api:pedido-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_categorias(self):
        """Prueba obtener la lista de categorías de ecommerce."""
        self.client.force_authenticate(user=self.user)
        url = reverse('api:categoriaecommerce-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['nombre'], 'Categoría Ecommerce')
    
    def test_get_productos(self):
        """Prueba obtener la lista de productos de ecommerce."""
        self.client.force_authenticate(user=self.user)
        url = reverse('api:productoecommerce-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['slug'], 'producto-prueba')
    
    def test_get_producto_detail(self):
        """Prueba obtener el detalle de un producto de ecommerce."""
        self.client.force_authenticate(user=self.user)
        url = reverse('api:productoecommerce-detail', kwargs={'slug': self.producto.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['slug'], 'producto-prueba')
        self.assertEqual(response.data['descripcion_corta'], 'Descripción corta')
    
    def test_registrar_visita(self):
        """Prueba registrar una visita a un producto."""
        self.client.force_authenticate(user=self.user)
        url = reverse('api:productoecommerce-registrar-visita', kwargs={'slug': self.producto.slug})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.visitas, 1)
    
    def test_get_carrito_actual(self):
        """Prueba obtener el carrito actual del usuario."""
        self.client.force_authenticate(user=self.user)
        url = reverse('api:carrito-actual')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_agregar_item_carrito(self):
        """Prueba agregar un item al carrito."""
        self.client.force_authenticate(user=self.user)
        url = reverse('api:carrito-agregar-item', args=[self.carrito.id])
        data = {
            'producto_id': self.producto_inv.id,
            'cantidad': 2
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ItemCarrito.objects.count(), 1)
    
    def test_crear_pedido_desde_carrito(self):
        """Prueba crear un pedido desde un carrito."""
        # Primero agregamos un item al carrito
        from django.contrib.contenttypes.models import ContentType
        content_type = ContentType.objects.get_for_model(Producto)
        
        item = ItemCarrito.objects.create(
            carrito=self.carrito,
            producto=self.producto_inv,
            content_type=content_type,
            object_id=self.producto_inv.id,
            cantidad=1,
            precio_unitario=150,
            _subtotal=150,
            _total=150
        )
        
        self.client.force_authenticate(user=self.user)
        url = reverse('api:pedido-crear-desde-carrito')
        data = {
            'carrito_id': self.carrito.id,
            'direccion_facturacion_id': self.direccion.id,
            'direccion_envio_id': self.direccion.id,
            'notas': 'Pedido de prueba'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Pedido.objects.count(), 1)
        
        # Verificar que el carrito se marcó como convertido a pedido
        self.carrito.refresh_from_db()
        self.assertTrue(self.carrito.convertido_a_pedido)
    
    def test_registrar_pago_pedido(self):
        """Prueba registrar un pago para un pedido."""
        # Primero creamos un pedido
        pedido = Pedido.objects.create(
            numero='PED-001',
            cliente=self.cliente,
            carrito=self.carrito,
            direccion_facturacion=self.direccion,
            direccion_envio=self.direccion,
            subtotal=150,
            total=150
        )
        
        self.client.force_authenticate(user=self.user)
        url = reverse('api:pedido-registrar-pago', args=[pedido.id])
        data = {
            'metodo': 'tarjeta',
            'monto': 150,
            'referencia': 'REF-001',
            'pasarela_id': 'PAYMENT-001',
            'estado': 'completado'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PagoOnline.objects.count(), 1)
    
    def test_cambiar_estado_pedido(self):
        """Prueba cambiar el estado de un pedido."""
        # Primero creamos un pedido
        pedido = Pedido.objects.create(
            numero='PED-001',
            cliente=self.cliente,
            carrito=self.carrito,
            direccion_facturacion=self.direccion,
            direccion_envio=self.direccion,
            subtotal=150,
            total=150,
            estado='pendiente'
        )
        
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('api:pedido-cambiar-estado', args=[pedido.id])
        data = {
            'estado': 'pagado'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        pedido.refresh_from_db()
        self.assertEqual(pedido.estado, 'pagado')