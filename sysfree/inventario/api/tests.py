from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from core.models import Usuario
from inventario.models import Categoria, Producto, Proveedor


class CategoriaTests(APITestCase):
    def setUp(self):
        # Crear un usuario para pruebas
        self.user = Usuario.objects.create_user(
            email='user@example.com',
            password='password123',
            nombres='User',
            apellidos='Test'
        )
        
        # Crear categorías para pruebas
        self.categoria = Categoria.objects.create(
            nombre='Categoría Test',
            codigo='CAT001',
            descripcion='Descripción de prueba'
        )
        
        # URL para obtener token
        self.token_url = '/api/token/'
        
        # Obtener token
        response = self.client.post(self.token_url, {
            'email': 'user@example.com',
            'password': 'password123'
        }, format='json')
        self.token = response.data['access']
    
    def test_obtener_lista_categorias(self):
        """
        Asegurar que se puede obtener la lista de categorías.
        """
        url = '/api/categorias/'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_crear_categoria(self):
        """
        Asegurar que se puede crear una categoría.
        """
        url = '/api/categorias/'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        data = {
            'nombre': 'Nueva Categoría',
            'codigo': 'CAT002',
            'descripcion': 'Nueva descripción'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Categoria.objects.count(), 2)


class ProductoTests(APITestCase):
    def setUp(self):
        # Crear un usuario para pruebas
        self.user = Usuario.objects.create_user(
            email='user@example.com',
            password='password123',
            nombres='User',
            apellidos='Test'
        )
        
        # Crear categoría para pruebas
        self.categoria = Categoria.objects.create(
            nombre='Categoría Test',
            codigo='CAT001',
            descripcion='Descripción de prueba'
        )
        
        # Crear producto para pruebas
        self.producto = Producto.objects.create(
            codigo='PROD001',
            nombre='Producto Test',
            descripcion='Descripción de prueba',
            precio_compra=10.00,
            precio_venta=15.00,
            stock=100,
            categoria=self.categoria
        )
        
        # URL para obtener token
        self.token_url = '/api/token/'
        
        # Obtener token
        response = self.client.post(self.token_url, {
            'email': 'user@example.com',
            'password': 'password123'
        }, format='json')
        self.token = response.data['access']
    
    def test_obtener_lista_productos(self):
        """
        Asegurar que se puede obtener la lista de productos.
        """
        url = '/api/productos/'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_registrar_entrada_inventario(self):
        """
        Asegurar que se puede registrar una entrada de inventario.
        """
        url = f'/api/productos/{self.producto.id}/registrar_entrada/'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        data = {
            'cantidad': 50,
            'origen': 'compra',
            'costo_unitario': 9.50,
            'documento': 'FACT-001',
            'notas': 'Entrada de prueba'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 150)  # 100 + 50
    
    def test_registrar_salida_inventario(self):
        """
        Asegurar que se puede registrar una salida de inventario.
        """
        url = f'/api/productos/{self.producto.id}/registrar_salida/'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        data = {
            'cantidad': 30,
            'origen': 'venta',
            'documento': 'FACT-V001',
            'notas': 'Salida de prueba'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 70)  # 100 - 30