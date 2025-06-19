from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from reparaciones.models import Reparacion, ServicioReparacion, DetalleServicio
from clientes.models import Cliente

User = get_user_model()


class ReparacionesAPITests(TestCase):
    """Pruebas para la API de reparaciones."""
    
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
        
        # Crear servicio de reparación
        self.servicio = ServicioReparacion.objects.create(
            nombre='Servicio de prueba',
            descripcion='Descripción de prueba',
            precio=100,
            tiempo_estimado=2,
            disponible_online=True,
            activo=True
        )
        
        # Crear reparación de prueba
        self.reparacion = Reparacion.objects.create(
            numero='REP-001',
            cliente=self.cliente,
            tipo_equipo='Laptop',
            marca='Marca de prueba',
            modelo='Modelo de prueba',
            problema_reportado='Problema de prueba',
            estado='recibido',
            costo_diagnostico=20,
            costo_reparacion=100,
            total=120,
            creado_por=self.user
        )
        
        # Crear detalle de servicio
        self.detalle_servicio = DetalleServicio.objects.create(
            reparacion=self.reparacion,
            servicio=self.servicio,
            precio=100,
            notas='Notas de prueba'
        )
        
        # Cliente API
        self.client = APIClient()
    
    def test_login_required(self):
        """Prueba que se requiera autenticación para acceder a la API."""
        response = self.client.get(reverse('api:reparacion-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_authenticated_user_can_access(self):
        """Prueba que un usuario autenticado pueda acceder a la API."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('api:reparacion-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_reparaciones(self):
        """Prueba obtener la lista de reparaciones."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('api:reparacion-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['numero'], 'REP-001')
    
    def test_get_reparacion_detail(self):
        """Prueba obtener el detalle de una reparación."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('api:reparacion-detail', args=[self.reparacion.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['numero'], 'REP-001')
        self.assertEqual(response.data['estado'], 'recibido')
    
    def test_create_reparacion(self):
        """Prueba crear una reparación."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'cliente': self.cliente.id,
            'tipo_equipo': 'PC',
            'marca': 'Otra marca',
            'modelo': 'Otro modelo',
            'problema_reportado': 'Otro problema',
            'estado': 'recibido',
            'costo_diagnostico': 30,
            'servicios': [
                {
                    'servicio': self.servicio.id,
                    'precio': 100,
                    'notas': 'Notas de servicio'
                }
            ]
        }
        response = self.client.post(reverse('api:reparacion-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reparacion.objects.count(), 2)
    
    def test_update_reparacion(self):
        """Prueba actualizar una reparación."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'estado': 'diagnostico',
            'diagnostico': 'Diagnóstico de prueba'
        }
        response = self.client.patch(
            reverse('api:reparacion-detail', args=[self.reparacion.id]),
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.reparacion.refresh_from_db()
        self.assertEqual(self.reparacion.estado, 'diagnostico')
        self.assertEqual(self.reparacion.diagnostico, 'Diagnóstico de prueba')
    
    def test_agregar_servicio(self):
        """Prueba agregar un servicio a una reparación."""
        self.client.force_authenticate(user=self.admin_user)
        # Crear otro servicio
        otro_servicio = ServicioReparacion.objects.create(
            nombre='Otro servicio',
            descripcion='Otra descripción',
            precio=50,
            tiempo_estimado=1,
            disponible_online=True,
            activo=True
        )
        
        data = {
            'servicio': otro_servicio.id,
            'precio': 50,
            'notas': 'Notas del nuevo servicio'
        }
        response = self.client.post(
            reverse('api:reparacion-agregar-servicio', args=[self.reparacion.id]),
            data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DetalleServicio.objects.count(), 2)
        
        # Verificar que el costo de reparación y total se actualizaron
        self.reparacion.refresh_from_db()
        self.assertEqual(self.reparacion.costo_reparacion, 150)  # 100 + 50
        self.assertEqual(self.reparacion.total, 170)  # 150 + 20 (diagnóstico)
    
    def test_cambiar_estado(self):
        """Prueba cambiar el estado de una reparación."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'estado': 'finalizado',
            'notas': 'Reparación completada'
        }
        response = self.client.post(
            reverse('api:reparacion-cambiar-estado', args=[self.reparacion.id]),
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.reparacion.refresh_from_db()
        self.assertEqual(self.reparacion.estado, 'finalizado')
    
    def test_get_servicios(self):
        """Prueba obtener la lista de servicios de reparación."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('api:servicioreparacion-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['nombre'], 'Servicio de prueba')