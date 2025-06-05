from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from reparaciones.models import Reparacion, SeguimientoReparacion, RepuestoReparacion, ServicioReparacion
from clientes.models import Cliente
from inventario.models import Producto, Categoria

User = get_user_model()


class ReparacionTest(TestCase):
    """Pruebas para el modelo Reparacion."""
    
    def setUp(self):
        # Crear usuario
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123'
        )
        
        # Crear técnico
        self.tecnico = User.objects.create_user(
            email='tecnico@example.com',
            password='password123'
        )
        
        # Crear cliente
        self.cliente = Cliente.objects.create(
            usuario=self.user,
            nombres='Cliente Reparacion Test',
            email='testreparacion@example.com',
            tipo_identificacion='cedula',
            identificacion='0000000007'
        )
        
        # Crear reparación
        self.reparacion = Reparacion.objects.create(
            numero='REP-12345',
            cliente=self.cliente,
            tipo_equipo='Laptop',
            marca='Test',
            modelo='X1',
            problema_reportado='No enciende',
            tecnico=self.tecnico,
            costo_diagnostico=Decimal('20.00'),
            costo_reparacion=Decimal('100.00'),
            costo_repuestos=Decimal('50.00')
        )
    
    def test_reparacion_creation(self):
        """Prueba la creación de una reparación."""
        self.assertEqual(self.reparacion.numero, 'REP-12345')
        self.assertEqual(self.reparacion.cliente, self.cliente)
        self.assertEqual(self.reparacion.tipo_equipo, 'Laptop')
        self.assertEqual(self.reparacion.estado, 'recibido')  # Estado por defecto
        self.assertEqual(self.reparacion.tecnico, self.tecnico)
    
    def test_calculo_total(self):
        """Prueba el cálculo del total de la reparación."""
        # El total debería ser la suma de diagnóstico, reparación y repuestos
        expected_total = Decimal('20.00') + Decimal('100.00') + Decimal('50.00')
        self.assertEqual(self.reparacion.total, expected_total)
        
        # Cambiar costos y verificar que el total se actualiza
        self.reparacion.costo_diagnostico = Decimal('30.00')
        self.reparacion.save()
        
        expected_total = Decimal('30.00') + Decimal('100.00') + Decimal('50.00')
        self.assertEqual(self.reparacion.total, expected_total)


class SeguimientoReparacionTest(TestCase):
    """Pruebas para el modelo SeguimientoReparacion."""
    
    def setUp(self):
        # Crear usuario
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123'
        )
        
        # Crear cliente
        self.cliente = Cliente.objects.create(
            usuario=self.user,
            nombres='Cliente Seguimiento Test',
            email='testseguimiento@example.com',
            tipo_identificacion='cedula',
            identificacion='0000000008'
        )
        
        # Crear reparación
        self.reparacion = Reparacion.objects.create(
            numero='REP-12345',
            cliente=self.cliente,
            tipo_equipo='Laptop',
            marca='Test',
            modelo='X1',
            problema_reportado='No enciende'
        )
        
        # Crear seguimiento
        self.seguimiento = SeguimientoReparacion.objects.create(
            reparacion=self.reparacion,
            estado_nuevo='diagnostico', # Corregido: estado -> estado_nuevo
            comentario='Se está realizando el diagnóstico', # Corregido: descripcion -> comentario
            creado_por=self.user # Corregido: usuario -> creado_por (asumiendo que se quiere asignar)
        )
    
    def test_seguimiento_creation(self):
        """Prueba la creación de un seguimiento."""
        self.assertEqual(self.seguimiento.reparacion, self.reparacion)
        self.assertEqual(self.seguimiento.estado_nuevo, 'diagnostico')
        self.assertEqual(self.seguimiento.comentario, 'Se está realizando el diagnóstico')
        self.assertEqual(self.seguimiento.creado_por, self.user)


class ServicioReparacionTest(TestCase):
    """Pruebas para el modelo ServicioReparacion."""
    
    def setUp(self):
        # Crear categoría
        self.categoria = Categoria.objects.create(
            nombre='Servicios',
            descripcion='Servicios de reparación'
        )
        
        # Crear producto asociado al servicio
        self.producto = Producto.objects.create(
            codigo='S001',
            nombre='Servicio de reparación',
            descripcion='Servicio de reparación',
            precio_compra=0,
            precio_venta=150,
            stock=0,
            categoria=self.categoria,
            es_inventariable=False,
            tipo='servicio'
        )
        
        # Crear servicio
        self.servicio = ServicioReparacion.objects.create(
            nombre='Reparación de laptop',
            descripcion='Servicio de reparación de laptop',
            tipo='reparacion',
            precio=150,
            tiempo_estimado=2,
            producto=self.producto,
            disponible_online=True
        )
    
    def test_servicio_creation(self):
        """Prueba la creación de un servicio."""
        self.assertEqual(self.servicio.nombre, 'Reparación de laptop')
        self.assertEqual(self.servicio.tipo, 'reparacion')
        self.assertEqual(self.servicio.precio, 150)
        self.assertEqual(self.servicio.tiempo_estimado, 2)
        self.assertEqual(self.servicio.producto, self.producto)
        self.assertTrue(self.servicio.disponible_online)
        self.assertFalse(self.servicio.requiere_diagnostico_previo)