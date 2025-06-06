from django.test import TestCase
from django.contrib.auth import get_user_model
from sysfree.clientes.models import Cliente, ContactoCliente, DireccionCliente
from sysfree.core.models import Usuario # Importa el modelo Usuario de core

class ClienteModelTest(TestCase):

    def setUp(self):
        """Configura un cliente de prueba para usar en los tests."""
        self.cliente_persona = Cliente.objects.create(
            tipo_identificacion='cedula',
            identificacion='1234567890',
            nombres='Juan',
            apellidos='Perez',
            tipo_cliente='persona',
            email='juan.perez@example.com',
            telefono='0987654321',
            celular='0998765432',
            direccion='Calle Falsa 123',
            fecha_nacimiento='1990-01-01',
            limite_credito=1000.00,
            dias_credito=30,
            recibir_promociones=True,
        )
        self.cliente_empresa = Cliente.objects.create(
            tipo_identificacion='ruc',
            identificacion='0987654321001',
            nombres='Empresa Test',
            nombre_comercial='ET S.A.',
            tipo_cliente='empresa',
            email='contacto@empresa.com',
            telefono='042345678',
            direccion='Avenida Principal 456',
            limite_credito=5000.00,
        )

    def test_creacion_cliente_persona(self):
        """Verifica la creación básica de un cliente tipo persona."""
        self.assertEqual(self.cliente_persona.tipo_identificacion, 'cedula')
        self.assertEqual(self.cliente_persona.identificacion, '1234567890')
        self.assertEqual(self.cliente_persona.nombres, 'Juan')
        self.assertEqual(self.cliente_persona.apellidos, 'Perez')
        self.assertEqual(self.cliente_persona.tipo_cliente, 'persona')
        self.assertEqual(str(self.cliente_persona), 'Juan Perez')
        self.assertEqual(self.cliente_persona.nombre_completo, 'Juan Perez')

    def test_creacion_cliente_empresa(self):
        """Verifica la creación básica de un cliente tipo empresa."""
        self.assertEqual(self.cliente_empresa.tipo_identificacion, 'ruc')
        self.assertEqual(self.cliente_empresa.identificacion, '0987654321001')
        self.assertEqual(self.cliente_empresa.nombres, 'Empresa Test')
        self.assertEqual(self.cliente_empresa.nombre_comercial, 'ET S.A.')
        self.assertEqual(self.cliente_empresa.tipo_cliente, 'empresa')
        self.assertEqual(str(self.cliente_empresa), 'ET S.A.')
        self.assertEqual(self.cliente_empresa.nombre_completo, 'ET S.A.')

    def test_cliente_sin_apellidos_persona(self):
        """Verifica el comportamiento de nombre_completo para persona sin apellidos."""
        cliente_sin_apellido = Cliente.objects.create(
            tipo_identificacion='cedula',
            identificacion='1111111111',
            nombres='Ana',
            tipo_cliente='persona',
        )
        self.assertEqual(cliente_sin_apellido.nombre_completo, 'Ana')

    def test_cliente_empresa_sin_nombre_comercial(self):
        """Verifica el comportamiento de nombre_completo para empresa sin nombre comercial."""
        cliente_empresa_sin_nombre_c = Cliente.objects.create(
            tipo_identificacion='ruc',
            identificacion='2222222222001',
            nombres='Otra Empresa',
            tipo_cliente='empresa',
        )
        self.assertEqual(cliente_empresa_sin_nombre_c.nombre_completo, 'Otra Empresa')


class ContactoClienteModelTest(TestCase):

    def setUp(self):
        """Configura un cliente y contactos de prueba."""
        self.cliente_empresa = Cliente.objects.create(
            tipo_identificacion='ruc',
            identificacion='0987654321001',
            nombres='Empresa Test',
            tipo_cliente='empresa',
        )
        self.contacto1 = ContactoCliente.objects.create(
            cliente=self.cliente_empresa,
            nombres='Contacto Uno',
            apellidos='Apellido Uno',
            es_principal=True,
        )
        self.contacto2 = ContactoCliente.objects.create(
            cliente=self.cliente_empresa,
            nombres='Contacto Dos',
            apellidos='Apellido Dos',
            es_principal=False,
        )

    def test_creacion_contacto(self):
        """Verifica la creación básica de un contacto."""
        self.assertEqual(self.contacto1.cliente, self.cliente_empresa)
        self.assertEqual(self.contacto1.nombres, 'Contacto Uno')
        self.assertEqual(self.contacto1.apellidos, 'Apellido Uno')
        self.assertTrue(self.contacto1.es_principal)
        self.assertEqual(str(self.contacto1), f'Contacto Uno Apellido Uno ({self.cliente_empresa})')

    def test_unico_contacto_principal_por_cliente(self):
        """Verifica que solo hay un contacto principal por cliente."""
        # Crear un nuevo contacto y marcarlo como principal
        contacto3 = ContactoCliente.objects.create(
            cliente=self.cliente_empresa,
            nombres='Contacto Tres',
            apellidos='Apellido Tres',
            es_principal=True,
        )

        # Recargar los contactos de la base de datos
        self.contacto1.refresh_from_db()
        self.contacto2.refresh_from_db()
        contacto3.refresh_from_db()

        self.assertFalse(self.contacto1.es_principal)
        self.assertFalse(self.contacto2.es_principal)
        self.assertTrue(contacto3.es_principal)


class DireccionClienteModelTest(TestCase):

    def setUp(self):
        """Configura un cliente y direcciones de prueba."""
        self.cliente = Cliente.objects.create(
            tipo_identificacion='cedula',
            identificacion='1234567890',
            nombres='Juan',
            apellidos='Perez',
            tipo_cliente='persona',
        )
        self.direccion_envio1 = DireccionCliente.objects.create(
            cliente=self.cliente,
            tipo='envio',
            direccion='Direccion de Envio 1',
            es_principal=True,
        )
        self.direccion_envio2 = DireccionCliente.objects.create(
            cliente=self.cliente,
            tipo='envio',
            direccion='Direccion de Envio 2',
            es_principal=False,
        )
        self.direccion_facturacion1 = DireccionCliente.objects.create(
            cliente=self.cliente,
            tipo='facturacion',
            direccion='Direccion de Facturacion 1',
            es_principal=True,
        )

    def test_creacion_direccion(self):
        """Verifica la creación básica de una dirección."""
        self.assertEqual(self.direccion_envio1.cliente, self.cliente)
        self.assertEqual(self.direccion_envio1.tipo, 'envio')
        self.assertEqual(self.direccion_envio1.direccion, 'Direccion de Envio 1')
        self.assertTrue(self.direccion_envio1.es_principal)
        self.assertIn(self.direccion_envio1.get_tipo_display(), str(self.direccion_envio1))

    def test_unico_direccion_principal_por_tipo_y_cliente(self):
        """Verifica que solo hay una dirección principal por tipo y cliente."""
        # Crear una nueva dirección de envío y marcarla como principal
        direccion_envio3 = DireccionCliente.objects.create(
            cliente=self.cliente,
            tipo='envio',
            direccion='Direccion de Envio 3',
            es_principal=True,
        )

        # Recargar las direcciones de la base de datos
        self.direccion_envio1.refresh_from_db()
        self.direccion_envio2.refresh_from_db()
        direccion_envio3.refresh_from_db()
        self.direccion_facturacion1.refresh_from_db()

        self.assertFalse(self.direccion_envio1.es_principal)
        self.assertFalse(self.direccion_envio2.es_principal)
        self.assertTrue(direccion_envio3.es_principal)
        self.assertTrue(self.direccion_facturacion1.es_principal) # La dirección de facturación no debería verse afectada

    def test_direccion_con_nombre(self):
        """Verifica el __str__ de una dirección con nombre."""
        direccion_con_nombre = DireccionCliente.objects.create(
            cliente=self.cliente,
            tipo='oficina',
            nombre='Oficina Principal',
            direccion='Direccion de Oficina',
        )
        self.assertIn("Oficina Principal", str(direccion_con_nombre))
        self.assertIn(direccion_con_nombre.get_tipo_display(), str(direccion_con_nombre))
