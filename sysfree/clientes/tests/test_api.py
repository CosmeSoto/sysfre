from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from clientes.models import Cliente, ContactoCliente, DireccionCliente

User = get_user_model()


class ClienteAPITests(TestCase):
    """Pruebas para la API de clientes."""
    
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
        
        # Crear contacto de prueba
        self.contacto = ContactoCliente.objects.create(
            cliente=self.cliente,
            nombres='Contacto',
            apellidos='Prueba',
            email='contacto@example.com',
            telefono='0987654322',
            es_principal=True
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
        
        # Cliente API
        self.client = APIClient()
    
    def test_login_required(self):
        """Prueba que se requiera autenticación para acceder a la API."""
        response = self.client.get(reverse('api:cliente-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_authenticated_user_can_access(self):
        """Prueba que un usuario autenticado pueda acceder a la API."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('api:cliente-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_clientes(self):
        """Prueba obtener la lista de clientes."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('api:cliente-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['nombres'], 'Cliente')
    
    def test_get_cliente_detail(self):
        """Prueba obtener el detalle de un cliente."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('api:cliente-detail', args=[self.cliente.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombres'], 'Cliente')
        self.assertEqual(response.data['apellidos'], 'Prueba')
    
    def test_create_cliente(self):
        """Prueba crear un cliente."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'tipo_identificacion': 'ruc',
            'identificacion': '0987654321',
            'nombres': 'Nuevo',
            'apellidos': 'Cliente',
            'email': 'nuevo@example.com',
            'telefono': '0987654323'
        }
        response = self.client.post(reverse('api:cliente-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Cliente.objects.count(), 2)
    
    def test_update_cliente(self):
        """Prueba actualizar un cliente."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'nombres': 'Cliente Actualizado',
            'email': 'actualizado@example.com'
        }
        response = self.client.patch(
            reverse('api:cliente-detail', args=[self.cliente.id]),
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.cliente.refresh_from_db()
        self.assertEqual(self.cliente.nombres, 'Cliente Actualizado')
        self.assertEqual(self.cliente.email, 'actualizado@example.com')
    
    def test_delete_cliente(self):
        """Prueba eliminar un cliente."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(
            reverse('api:cliente-detail', args=[self.cliente.id])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Cliente.objects.count(), 0)
    
    def test_buscar_clientes(self):
        """Prueba el endpoint de búsqueda de clientes."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            reverse('api:cliente-buscar'),
            {'termino': 'Cliente'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nombres'], 'Cliente')
    
    def test_agregar_contacto(self):
        """Prueba agregar un contacto a un cliente."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'cliente': self.cliente.id,  # Agregamos el cliente_id
            'nombres': 'Nuevo',
            'apellidos': 'Contacto',
            'email': 'nuevo_contacto@example.com',
            'telefono': '0987654324',
            'es_principal': False
        }
        response = self.client.post(
            reverse('api:cliente-agregar-contacto', args=[self.cliente.id]),
            data
        )
        if response.status_code != status.HTTP_201_CREATED:
            print("Error en agregar_contacto:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ContactoCliente.objects.count(), 2)
    
    def test_agregar_direccion(self):
        """Prueba agregar una dirección a un cliente."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'cliente': self.cliente.id,  # Agregamos el cliente_id
            'tipo': 'envio',
            'direccion': 'Calle Secundaria 456',
            'ciudad': 'Ciudad Prueba',
            'provincia': 'Provincia Prueba',
            'es_principal': True
        }
        response = self.client.post(
            reverse('api:cliente-agregar-direccion', args=[self.cliente.id]),
            data
        )
        if response.status_code != status.HTTP_201_CREATED:
            print("Error en agregar_direccion:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DireccionCliente.objects.count(), 2)