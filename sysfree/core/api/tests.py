from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from core.models import Usuario, Empresa, Sucursal


class UsuarioTests(APITestCase):
    def setUp(self):
        # Crear un superusuario para pruebas
        self.admin = Usuario.objects.create_superuser(
            email='admin@example.com',
            password='password123',
            nombres='Admin',
            apellidos='Test'
        )
        
        # Crear un usuario normal para pruebas
        self.user = Usuario.objects.create_user(
            email='user@example.com',
            password='password123',
            nombres='User',
            apellidos='Test'
        )
        
        # URL para obtener token
        self.token_url = '/api/token/'
        
        # Obtener token para admin
        response = self.client.post(self.token_url, {
            'email': 'admin@example.com',
            'password': 'password123'
        }, format='json')
        self.admin_token = response.data['access']
        
        # Obtener token para usuario normal
        response = self.client.post(self.token_url, {
            'email': 'user@example.com',
            'password': 'password123'
        }, format='json')
        self.user_token = response.data['access']
    
    def test_obtener_lista_usuarios_como_admin(self):
        """
        Asegurar que un admin puede obtener la lista de usuarios.
        """
        url = '/api/usuarios/'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Admin y usuario normal
    
    def test_obtener_lista_usuarios_como_usuario_normal(self):
        """
        Asegurar que un usuario normal no puede obtener la lista completa de usuarios.
        """
        url = '/api/usuarios/'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_crear_usuario_como_admin(self):
        """
        Asegurar que un admin puede crear usuarios.
        """
        url = '/api/usuarios/'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        data = {
            'email': 'nuevo@example.com',
            'password': 'password123',
            'nombres': 'Nuevo',
            'apellidos': 'Usuario'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Usuario.objects.count(), 3)
    
    def test_crear_usuario_como_usuario_normal(self):
        """
        Asegurar que un usuario normal no puede crear usuarios.
        """
        url = '/api/usuarios/'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        data = {
            'email': 'nuevo@example.com',
            'password': 'password123',
            'nombres': 'Nuevo',
            'apellidos': 'Usuario'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class EmpresaTests(APITestCase):
    def setUp(self):
        # Crear un superusuario para pruebas
        self.admin = Usuario.objects.create_superuser(
            email='admin@example.com',
            password='password123',
            nombres='Admin',
            apellidos='Test'
        )
        
        # Crear una empresa para pruebas
        self.empresa = Empresa.objects.create(
            nombre='Empresa Test',
            ruc='1234567890001',
            direccion='Dirección Test',
            telefono='123456789',
            email='empresa@test.com'
        )
        
        # URL para obtener token
        self.token_url = '/api/token/'
        
        # Obtener token para admin
        response = self.client.post(self.token_url, {
            'email': 'admin@example.com',
            'password': 'password123'
        }, format='json')
        self.admin_token = response.data['access']
    
    def test_obtener_lista_empresas(self):
        """
        Asegurar que se puede obtener la lista de empresas.
        """
        url = '/api/empresas/'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_crear_empresa(self):
        """
        Asegurar que se puede crear una empresa.
        """
        url = '/api/empresas/'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        data = {
            'nombre': 'Nueva Empresa',
            'ruc': '0987654321001',
            'direccion': 'Nueva Dirección',
            'telefono': '987654321',
            'email': 'nueva@empresa.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Empresa.objects.count(), 2)
    
    def test_actualizar_empresa(self):
        """
        Asegurar que se puede actualizar una empresa.
        """
        url = f'/api/empresas/{self.empresa.id}/'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        data = {
            'nombre': 'Empresa Actualizada',
            'ruc': '1234567890001',
            'direccion': 'Dirección Actualizada',
            'telefono': '123456789',
            'email': 'empresa@test.com'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.empresa.refresh_from_db()
        self.assertEqual(self.empresa.nombre, 'Empresa Actualizada')
        self.assertEqual(self.empresa.direccion, 'Dirección Actualizada')