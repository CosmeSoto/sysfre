from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from ventas.models import Venta
from clientes.models import Cliente
from inventario.models import Producto, Categoria, MovimientoInventario, Almacen

User = get_user_model()


class ReportesAPITests(TestCase):
    """Pruebas para la API de reportes."""
    
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
        
        # Crear almacén de prueba
        self.almacen = Almacen.objects.create(
            nombre='Almacén de prueba',
            direccion='Dirección de prueba'
        )
        
        # Crear movimiento de inventario
        self.movimiento = MovimientoInventario.objects.create(
            tipo='entrada',
            origen='compra',
            producto=self.producto,
            cantidad=5,
            stock_anterior=5,
            stock_nuevo=10,
            costo_unitario=100,
            almacen=self.almacen,
            creado_por=self.user
        )
        
        # Cliente API
        self.client = APIClient()
    
    def test_login_required(self):
        """Prueba que se requiera autenticación para acceder a la API."""
        response = self.client.get(reverse('api:reportes-ventas'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_authenticated_user_can_access(self):
        """Prueba que un usuario autenticado pueda acceder a la API."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('api:reportes-ventas'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_reporte_ventas(self):
        """Prueba obtener el reporte de ventas."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('api:reportes-ventas'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_ventas', response.data)
        self.assertIn('ventas_por_mes', response.data)
    
    def test_reporte_ventas_por_periodo(self):
        """Prueba obtener el reporte de ventas por periodo."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            reverse('api:reportes-ventas-por-periodo'),
            {'fecha_inicio': self.venta.fecha.strftime('%Y-%m-%d'),
             'fecha_fin': self.venta.fecha.strftime('%Y-%m-%d')}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_ventas', response.data)
        self.assertIn('ventas', response.data)
    
    def test_reporte_productos_mas_vendidos(self):
        """Prueba obtener el reporte de productos más vendidos."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('api:reportes-productos-mas-vendidos'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('productos', response.data)
    
    def test_reporte_clientes_frecuentes(self):
        """Prueba obtener el reporte de clientes frecuentes."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('api:reportes-clientes-frecuentes'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('clientes', response.data)
    
    def test_reporte_inventario(self):
        """Prueba obtener el reporte de inventario."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('api:reportes-inventario'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('productos', response.data)
    
    def test_reporte_movimientos_inventario(self):
        """Prueba obtener el reporte de movimientos de inventario."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            reverse('api:reportes-movimientos-inventario'),
            {'producto_id': self.producto.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('movimientos', response.data)
        self.assertEqual(len(response.data['movimientos']), 1)
    
    def test_reporte_productos_bajo_stock(self):
        """Prueba obtener el reporte de productos con bajo stock."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('api:reportes-productos-bajo-stock'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('productos', response.data)