from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from inventario.models import Producto, Categoria

User = get_user_model()


class APITests(TestCase):
    """Pruebas para la API."""
    
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
        self.assertEqual(response.data['categoria_nombre'], 'Categoría de prueba')
    
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
    
    def test_buscar_productos(self):
        """Prueba el endpoint de búsqueda de productos."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            reverse('api:producto-list'), # Usar la URL de la lista
            {'search': 'prueba'} # El parámetro es 'search'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1) # Los resultados están paginados
        self.assertEqual(response.data['results'][0]['nombre'], 'Producto de prueba')
    
    def test_actualizar_stock(self):
        """Prueba el endpoint para actualizar el stock de un producto."""
        self.client.force_authenticate(user=self.admin_user)
        
        # Crear un almacén para las pruebas
        from inventario.models import Almacen, StockAlmacen
        almacen = Almacen.objects.create(
            nombre='Almacén de prueba',
            direccion='Dirección de prueba'
        )
        
        # Crear stock inicial en el almacén
        StockAlmacen.objects.create(
            producto=self.producto,
            almacen=almacen,
            cantidad=0  # Inicialmente sin stock en el almacén
        )
        
        # Registrar entrada de stock
        response = self.client.post(
            reverse('api:producto-registrar-entrada', args=[self.producto.id]),
            {
                'cantidad': 5, 
                'origen': 'ajuste', 
                'costo_unitario': self.producto.precio_compra,
                'almacen': almacen.id
            }
        )
        if response.status_code != status.HTTP_201_CREATED:
            print("Error en registrar_entrada:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verificar que el stock en el almacén se actualizó correctamente
        stock_almacen = StockAlmacen.objects.get(producto=self.producto, almacen=almacen)
        self.assertEqual(stock_almacen.cantidad, 5)
        
        # Verificar que el stock total del producto se actualizó correctamente
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 5)  # El stock ahora es 5 (solo hay stock en este almacén)
        
        # Probar salida de stock
        response = self.client.post(
            reverse('api:producto-registrar-salida', args=[self.producto.id]),
            {
                'cantidad': 3, 
                'origen': 'ajuste',
                'almacen': almacen.id
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verificar que el stock en el almacén se actualizó correctamente
        stock_almacen.refresh_from_db()
        self.assertEqual(stock_almacen.cantidad, 2)
        
        # Verificar que el stock total del producto se actualizó correctamente
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 2)  # 5 - 3 = 2