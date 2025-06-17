from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from ventas.models import Venta, DetalleVenta, Pago
from clientes.models import Cliente, DireccionCliente
from inventario.models import Producto, Categoria

User = get_user_model()


class VentasAPITests(TestCase):
    """Pruebas para la API de ventas."""
    
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
            telefono='0987654321'
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
        
        # Crear categoría de prueba
        self.categoria = Categoria.objects.create(
            nombre='Categoría de prueba',
            descripcion='Descripción de prueba'
        )
        
        # Crear producto de prueba
        self.producto = Producto.objects.create(
            codigo='P001',
            nombre='Producto de prueba',
            descripcion='Descripción de prueba',
            precio_compra=100,
            precio_venta=150,
            stock=10,
            categoria=self.categoria
        )
        
        # Crear venta de prueba
        self.venta = Venta.objects.create(
            numero='FAC-001',
            cliente=self.cliente,
            tipo='factura',
            estado='borrador',
            subtotal=150,
            total=150,
            creado_por=self.user,
            modificado_por=self.user
        )
        
        # Crear detalle de venta
        self.detalle = DetalleVenta.objects.create(
            venta=self.venta,
            producto=self.producto,
            cantidad=1,
            precio_unitario=150,
            subtotal=150,
            total=150,
            creado_por=self.user,
            modificado_por=self.user
        )
        
        # Cliente API
        self.client = APIClient()
    
    def test_login_required(self):
        """Prueba que se requiera autenticación para acceder a la API."""
        response = self.client.get(reverse('api:venta-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_authenticated_user_can_access(self):
        """Prueba que un usuario autenticado pueda acceder a la API."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('api:venta-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_ventas(self):
        """Prueba obtener la lista de ventas."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('api:venta-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['numero'], 'FAC-001')
    
    def test_get_venta_detail(self):
        """Prueba obtener el detalle de una venta."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('api:venta-detail', args=[self.venta.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['numero'], 'FAC-001')
        self.assertEqual(response.data['estado'], 'borrador')
    
    def test_crear_venta(self):
        """Prueba crear una venta."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'cliente_id': self.cliente.id,
            'tipo': 'factura',
            'items': [
                {
                    'producto_id': self.producto.id,
                    'cantidad': 2,
                    'precio_unitario': 150
                }
            ],
            'direccion_facturacion_id': self.direccion.id,
            'notas': 'Venta de prueba'
        }
        response = self.client.post(reverse('api:venta-crear-venta'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Venta.objects.count(), 2)
    
    def test_registrar_pago(self):
        """Prueba registrar un pago para una venta."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'metodo': 'efectivo',
            'monto': 150,
            'referencia': 'REF-001'
        }
        response = self.client.post(
            reverse('api:venta-registrar-pago', args=[self.venta.id]),
            data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Pago.objects.count(), 1)
    
    def test_cambiar_estado(self):
        """Prueba cambiar el estado de una venta."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'estado': 'pagada'
        }
        response = self.client.post(
            reverse('api:venta-cambiar-estado', args=[self.venta.id]),
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.venta.refresh_from_db()
        self.assertEqual(self.venta.estado, 'pagada')
    
    def test_get_detalles_venta(self):
        """Prueba obtener los detalles de una venta."""
        self.client.force_authenticate(user=self.user)
        
        # Usar la URL de la venta para obtener los detalles
        url = reverse('api:venta-detail', args=[self.venta.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detalles', response.data)
        detalles = response.data['detalles']
        self.assertEqual(len(detalles), 1)
        self.assertEqual(float(detalles[0]['cantidad']), 1.0)
        self.assertEqual(detalles[0]['precio_unitario'], '150.00')