from django.test import TestCase
from django.contrib.auth import get_user_model
from sysfree.clientes.models import Cliente, ContactoCliente, DireccionCliente
from sysfree.core.models import Usuario # Assuming Usuario model is in core app

class ClienteModelTest(TestCase):

    def setUp(self):
        """Set up non-modified objects for every test method."""
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

    def test_cliente_creation_persona(self):
        """Test creation of a Cliente of type persona."""
        self.assertEqual(self.cliente_persona.tipo_identificacion, 'cedula')
        self.assertEqual(self.cliente_persona.identificacion, '1234567890')
        self.assertEqual(self.cliente_persona.nombres, 'Juan')
        self.assertEqual(self.cliente_persona.apellidos, 'Perez')
        self.assertEqual(self.cliente_persona.tipo_cliente, 'persona')
        self.assertEqual(self.cliente_persona.email, 'juan.perez@example.com')
        self.assertEqual(self.cliente_persona.telefono, '0987654321')
        self.assertEqual(self.cliente_persona.celular, '0998765432')
        self.assertEqual(self.cliente_persona.direccion, 'Calle Falsa 123')
        self.assertEqual(str(self.cliente_persona), 'Juan Perez')
        self.assertEqual(self.cliente_persona.nombre_completo, 'Juan Perez')

    def test_cliente_creation_empresa(self):
        """Test creation of a Cliente of type empresa."""
        self.assertEqual(self.cliente_empresa.tipo_identificacion, 'ruc')
        self.assertEqual(self.cliente_empresa.identificacion, '0987654321001')
        self.assertEqual(self.cliente_empresa.nombres, 'Empresa Test')
        self.assertEqual(self.cliente_empresa.nombre_comercial, 'ET S.A.')
        self.assertEqual(self.cliente_empresa.tipo_cliente, 'empresa')
        self.assertEqual(self.cliente_empresa.email, 'contacto@empresa.com')
        self.assertEqual(self.cliente_empresa.telefono, '042345678')
        self.assertEqual(str(self.cliente_empresa), 'ET S.A.')
        self.assertEqual(self.cliente_empresa.nombre_completo, 'ET S.A.')

    def test_cliente_str_persona_no_apellidos(self):
        """Test the string representation of a persona client without last name."""
        cliente = Cliente.objects.create(
            tipo_identificacion='cedula',
            identificacion='1111111111',
            nombres='Ana',
            tipo_cliente='persona',
        )
        self.assertEqual(str(cliente), 'Ana')
        self.assertEqual(cliente.nombre_completo, 'Ana')

    def test_cliente_str_empresa_no_nombre_comercial(self):
        """Test the string representation of an empresa client without commercial name."""
        cliente = Cliente.objects.create(
            tipo_identificacion='ruc',
            identificacion='2222222222001',
            nombres='Otra Empresa',
            tipo_cliente='empresa',
        )
        self.assertEqual(str(cliente), 'Otra Empresa')
        self.assertEqual(cliente.nombre_completo, 'Otra Empresa')

    def test_cliente_tiene_acceso_portal(self):
        """Test the tiene_acceso_portal property."""
        User = get_user_model()
        user = User.objects.create_user(username='testuser', password='password')
        self.cliente_persona.usuario = user
        self.cliente_persona.save()
        self.assertTrue(self.cliente_persona.tiene_acceso_portal)

        self.cliente_persona.usuario = None
        self.cliente_persona.save()
        self.assertFalse(self.cliente_persona.tiene_acceso_portal)


class ContactoClienteModelTest(TestCase):

    def setUp(self):
        """Set up a client and contact objects for every test method."""
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
            cargo='Gerente',
            email='contacto1@empresa.com',
            telefono='111111111',
            celular='222222222',
            notas='Nota 1'
        )
        self.contacto2 = ContactoCliente.objects.create(
            cliente=self.cliente_empresa,
            nombres='Contacto Dos',
            apellidos='Apellido Dos',
            es_principal=False,
        )

    def test_contacto_creation(self):
        """Test creation of a ContactoCliente."""
        self.assertEqual(self.contacto1.cliente, self.cliente_empresa)
        self.assertEqual(self.contacto1.nombres, 'Contacto Uno')
        self.assertEqual(self.contacto1.apellidos, 'Apellido Uno')
        self.assertTrue(self.contacto1.es_principal)
        self.assertEqual(self.contacto1.cargo, 'Gerente')
        self.assertEqual(self.contacto1.email, 'contacto1@empresa.com')
        self.assertEqual(self.contacto1.telefono, '111111111')
        self.assertEqual(self.contacto1.celular, '222222222')
        self.assertEqual(self.contacto1.notas, 'Nota 1')

    def test_contacto_str(self):
        """Test the string representation of a ContactoCliente."""
        self.assertEqual(str(self.contacto1), f'Contacto Uno Apellido Uno ({self.cliente_empresa})')

    def test_unique_principal_contact_per_client(self):
        """Test that only one contact is principal per client."""
        # Create a new contact and mark it as principal
        contacto3 = ContactoCliente.objects.create(
            cliente=self.cliente_empresa,
            nombres='Contacto Tres',
            apellidos='Apellido Tres',
            es_principal=True,
        )

        # Refresh contacts from db to see the changes made by save method
        self.contacto1.refresh_from_db()
        self.contacto2.refresh_from_db()
        contacto3.refresh_from_db()

        self.assertFalse(self.contacto1.es_principal)
        self.assertFalse(self.contacto2.es_principal)
        self.assertTrue(contacto3.es_principal)

    def test_saving_non_principal_contact(self):
        """Test saving a non-principal contact doesn't change other principals."""
        contacto4 = ContactoCliente.objects.create(
            cliente=self.cliente_empresa,
            nombres='Contacto Cuatro',
            apellidos='Apellido Cuatro',
            es_principal=False,
        )
        self.contacto1.refresh_from_db()
        self.assertTrue(self.contacto1.es_principal) # Should still be principal


class DireccionClienteModelTest(TestCase):

    def setUp(self):
        """Set up a client and address objects for every test method."""
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
            nombre='Casa Principal',
            direccion='Direccion de Envio 1',
            ciudad='Ciudad 1',
            provincia='Provincia 1',
            codigo_postal='12345',
            es_principal=True,
            notas='Nota Direccion 1',
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

    def test_direccion_creation(self):
        """Test creation of a DireccionCliente."""
        self.assertEqual(self.direccion_envio1.cliente, self.cliente)
        self.assertEqual(self.direccion_envio1.tipo, 'envio')
        self.assertEqual(self.direccion_envio1.nombre, 'Casa Principal')
        self.assertEqual(self.direccion_envio1.direccion, 'Direccion de Envio 1')
        self.assertEqual(self.direccion_envio1.ciudad, 'Ciudad 1')
        self.assertEqual(self.direccion_envio1.provincia, 'Provincia 1')
        self.assertEqual(self.direccion_envio1.codigo_postal, '12345')
        self.assertTrue(self.direccion_envio1.es_principal)
        self.assertEqual(self.direccion_envio1.notas, 'Nota Direccion 1')

    def test_direccion_str_with_name(self):
        """Test the string representation of a DireccionCliente with a name."""
        self.assertEqual(str(self.direccion_envio1), f'Casa Principal ({self.direccion_envio1.get_tipo_display()}) - {self.cliente}')

    def test_direccion_str_without_name(self):
        """Test the string representation of a DireccionCliente without a name."""
        self.assertEqual(str(self.direccion_envio2), f'{self.direccion_envio2.get_tipo_display()} - {self.cliente}')

    def test_unique_principal_address_per_type_and_client(self):
        """Test that only one address is principal per type and client."""
        # Create a new shipping address and mark it as principal
        direccion_envio3 = DireccionCliente.objects.create(
            cliente=self.cliente,
            tipo='envio',
            direccion='Direccion de Envio 3',
            es_principal=True,
        )

        # Refresh addresses from db to see the changes made by save method
        self.direccion_envio1.refresh_from_db()
        self.direccion_envio2.refresh_from_db()
        direccion_envio3.refresh_from_db()
        self.direccion_facturacion1.refresh_from_db()

        self.assertFalse(self.direccion_envio1.es_principal)
        self.assertFalse(self.direccion_envio2.es_principal)
        self.assertTrue(direccion_envio3.es_principal)
        self.assertTrue(self.direccion_facturacion1.es_principal) # Facturacion address should not be affected

    def test_saving_non_principal_address(self):
        """Test saving a non-principal address doesn't change other principals."""
        direccion_envio4 = DireccionCliente.objects.create(
            cliente=self.cliente,
            tipo='envio',
            direccion='Direccion de Envio 4',
            es_principal=False,
        )
        self.direccion_envio1.refresh_from_db()
        self.assertTrue(self.direccion_envio1.es_principal) # Should still be principal

    def test_latitude_longitude_fields(self):
        """Test creation with latitude and longitude."""
        direccion_geo = DireccionCliente.objects.create(
            cliente=self.cliente,
            tipo='otro',
            direccion='Direccion con Geo',
            latitud=10.1234567,
            longitud=-20.7654321,
        )
        self.assertEqual(direccion_geo.latitud, 10.1234567)
        self.assertEqual(direccion_geo.longitud, -20.7654321)