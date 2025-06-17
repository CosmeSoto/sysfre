from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from fiscal.models import Impuesto, Retencion, ComprobanteRetencion
from ventas.models import Venta
from clientes.models import Cliente
from inventario.models import Producto, Categoria

User = get_user_model()


class FiscalAPITests(TestCase):
    """Pruebas para la API fiscal."""
    
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
            estado='pagada',
            subtotal=150,
            total=150,
            creado_por=self.user,
            modificado_por=self.user
        )
        
        # Crear impuesto de prueba
        self.impuesto = Impuesto.objects.create(
            codigo='IVA',
            nombre='IVA',
            porcentaje=12,
            activo=True
        )
        
        # Crear retención de prueba
        self.retencion = Retencion.objects.create(
            codigo='RET-IVA',
            nombre='Retención IVA',
            porcentaje=30,
            tipo='iva',
            activo=True
        )
        
        # Crear comprobante de retención
        self.comprobante = ComprobanteRetencion.objects.create(
            numero='RET-001',
            venta=self.venta,
            fecha_emision=self.venta.fecha,
            base_imponible=150,
            total_retenido=5.4,  # 30% del IVA (12% de 150 = 18, 30% de 18 = 5.4)
            creado_por=self.user,
            modificado_por=self.user
        )
        
        # Cliente API
        self.client = APIClient()
    
    def test_login_required(self):
        """Prueba que se requiera autenticación para acceder a la API."""
        response = self.client.get(reverse('api:impuesto-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_authenticated_user_can_access(self):
        """Prueba que un usuario autenticado pueda acceder a la API."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('api:impuesto-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_impuestos(self):
        """Prueba obtener la lista de impuestos."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('api:impuesto-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['codigo'], 'IVA')
    
    def test_get_impuesto_detail(self):
        """Prueba obtener el detalle de un impuesto."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('api:impuesto-detail', args=[self.impuesto.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['codigo'], 'IVA')
        self.assertEqual(response.data['porcentaje'], 12)
    
    def test_create_impuesto(self):
        """Prueba crear un impuesto."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'codigo': 'ICE',
            'nombre': 'Impuesto a Consumos Especiales',
            'porcentaje': 15,
            'activo': True
        }
        response = self.client.post(reverse('api:impuesto-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Impuesto.objects.count(), 2)
    
    def test_update_impuesto(self):
        """Prueba actualizar un impuesto."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'porcentaje': 14
        }
        response = self.client.patch(
            reverse('api:impuesto-detail', args=[self.impuesto.id]),
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.impuesto.refresh_from_db()
        self.assertEqual(self.impuesto.porcentaje, 14)
    
    def test_get_retenciones(self):
        """Prueba obtener la lista de retenciones."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('api:retencion-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['codigo'], 'RET-IVA')
    
    def test_get_comprobantes(self):
        """Prueba obtener la lista de comprobantes de retención."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('api:comprobanteretencion-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['numero'], 'RET-001')
    
    def test_create_comprobante(self):
        """Prueba crear un comprobante de retención."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'venta': self.venta.id,
            'fecha_emision': self.venta.fecha.strftime('%Y-%m-%d'),
            'base_imponible': 200,
            'total_retenido': 7.2,
            'retenciones': [
                {
                    'retencion': self.retencion.id,
                    'base_imponible': 200,
                    'valor': 7.2
                }
            ]
        }
        response = self.client.post(reverse('api:comprobanteretencion-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ComprobanteRetencion.objects.count(), 2)