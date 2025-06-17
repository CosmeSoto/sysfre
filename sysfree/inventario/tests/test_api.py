from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from inventario.models import Categoria, Producto, Proveedor, Almacen, StockAlmacen

User = get_user_model()


class InventarioAPITests(TestCase):
    """Pruebas para la API de inventario."""
    
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
        
        # Crear proveedor de prueba
        self.proveedor = Proveedor.objects.create(
            nombre='Proveedor de prueba',
            ruc='1234567890001',
            email='proveedor@example.com',
            telefono='0987654321'
        )
        
        # Crear almacén de prueba
        self.almacen = Almacen.objects.create(
            nombre='Almacén de prueba',
            direccion='Dirección de prueba'
        )
        
        # Crear stock en almacén
        self.stock_almacen = StockAlmacen.objects.create(
            producto=self.producto,
            almacen=self.almacen,
            cantidad=10
        )
        
        # Cliente API
        self.client = APIClient()
    
    def test_login_required(self):
        """Prueba que se requiera autenticación para acceder a la API."""
        response = self.client.get(reverse('api:producto-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_authenticated_user_can_access(self):
        """Prueba que un usuario autenticado pueda acceder a la API."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('api:producto-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_productos(self):
        """Prueba obtener la lista de productos."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('api:producto-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['nombre'], 'Producto de prueba')
    
    def test_get_producto_detail(self):
        """Prueba obtener el detalle de un producto."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('api:producto-detail', args=[self.producto.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre'], 'Producto de prueba')
    
    def test_create_producto(self):
        """Prueba crear un producto."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'codigo': 'P002',
            'nombre': 'Nuevo producto',
            'descripcion': 'Nueva descripción',
            'precio_compra': 200,
            'precio_venta': 300,
            'stock': 5,
            'categoria': self.categoria.id
        }
        response = self.client.post(reverse('api:producto-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Producto.objects.count(), 2)
    
    def test_update_producto(self):
        """Prueba actualizar un producto."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'nombre': 'Producto actualizado',
            'precio_venta': 200
        }
        response = self.client.patch(
            reverse('api:producto-detail', args=[self.producto.id]),
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.nombre, 'Producto actualizado')
        self.assertEqual(self.producto.precio_venta, 200)
    
    def test_delete_producto(self):
        """Prueba eliminar un producto."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(
            reverse('api:producto-detail', args=[self.producto.id])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Producto.objects.count(), 0)
    
    def test_registrar_entrada(self):
        """Prueba el endpoint para registrar entrada de inventario."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'cantidad': 5,
            'costo_unitario': 100,
            'almacen': self.almacen.id,
            'proveedor': self.proveedor.id,
            'origen': 'compra',
            'documento': 'FAC-001',
            'notas': 'Entrada de prueba'
        }
        response = self.client.post(
            reverse('api:producto-registrar-entrada', args=[self.producto.id]),
            data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 15)  # 10 + 5
    
    def test_registrar_salida(self):
        """Prueba el endpoint para registrar salida de inventario."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'cantidad': 3,
            'almacen': self.almacen.id,
            'origen': 'venta',
            'documento': 'FAC-001',
            'notas': 'Salida de prueba'
        }
        response = self.client.post(
            reverse('api:producto-registrar-salida', args=[self.producto.id]),
            data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 7)  # 10 - 3
    
    def test_get_categorias(self):
        """Prueba obtener la lista de categorías."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('api:categoria-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['nombre'], 'Categoría de prueba')
    
    def test_get_proveedores(self):
        """Prueba obtener la lista de proveedores."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('api:proveedor-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['nombre'], 'Proveedor de prueba')