from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.utils import IntegrityError
from datetime import date, timedelta
from decimal import Decimal
from reparaciones.models import Reparacion, SeguimientoReparacion, ServicioReparacion, RepuestoReparacion, GarantiaReparacion, CitaServicio
from clientes.models import Cliente
from core.models import Usuario
from inventario.models import Producto, Categoria
from ventas.models import Venta, DetalleVenta
from core.services import IVAService

class ReparacionModelTest(TestCase):
    """
    Pruebas para el modelo Reparacion.
    """
    def setUp(self):
        self.cliente = Cliente.objects.create(
            tipo_identificacion='cedula',
            identificacion='1234567890',
            nombres='Juan',
            apellidos='Perez',
            tipo_cliente='persona'
        )
        self.tecnico = Usuario.objects.create_user(
            email='tecnico@example.com',
            password='testpass123',
            nombres='Carlos',
            apellidos='Gomez'
        )
        self.categoria = Categoria.objects.create(nombre='Electrónica')
        self.producto = Producto.objects.create(
            codigo='REP001',
            nombre='Pantalla LCD',
            categoria=self.categoria,
            precio_venta=50.00,
            stock=10.00,
            es_inventariable=True
        )

    def test_reparacion_creacion(self):
        """
        Verifica la creación de una reparación.
        """
        reparacion = Reparacion.objects.create(
            numero='REP001',
            cliente=self.cliente,
            tipo_equipo='Laptop',
            marca='Dell',
            modelo='XPS 13',
            problema_reportado='Pantalla no enciende',
            estado='recibido',
            prioridad='media',
            tecnico=self.tecnico,
            costo_diagnostico=20.00,
            costo_reparacion=100.00,
            costo_repuestos=50.00,
            public_url='https://freecom.com/reparacion/rep001'
        )
        self.assertEqual(reparacion.numero, 'REP001')
        self.assertEqual(reparacion.cliente, self.cliente)
        self.assertEqual(reparacion.tipo_equipo, 'Laptop')
        self.assertEqual(reparacion.marca, 'Dell')
        self.assertEqual(reparacion.modelo, 'XPS 13')
        self.assertEqual(reparacion.problema_reportado, 'Pantalla no enciende')
        self.assertEqual(reparacion.estado, 'recibido')
        self.assertEqual(reparacion.prioridad, 'media')
        self.assertEqual(reparacion.tecnico, self.tecnico)
        self.assertEqual(float(reparacion.costo_diagnostico), 20.00)
        self.assertEqual(float(reparacion.costo_reparacion), 100.00)
        self.assertEqual(float(reparacion.costo_repuestos), 50.00)
        self.assertEqual(float(reparacion.total), 170.00)  # 20 + 100 + 50
        self.assertFalse(reparacion.facturado)
        self.assertIsNone(reparacion.factura)
        self.assertEqual(reparacion.public_url, 'https://freecom.com/reparacion/rep001')
        self.assertIsNotNone(reparacion.fecha_recepcion)
        self.assertTrue(isinstance(reparacion, Reparacion))

    def test_reparacion_str(self):
        """
        Verifica el método __str__ de Reparacion.
        """
        reparacion = Reparacion.objects.create(
            numero='REP001',
            cliente=self.cliente,
            tipo_equipo='Laptop',
            marca='Dell'
        )
        self.assertEqual(str(reparacion), f"REP001 - {self.cliente} - Laptop Dell")

    def test_reparacion_numero_unico(self):
        """
        Verifica que el campo numero sea único.
        """
        Reparacion.objects.create(numero='REP001', cliente=self.cliente)
        with self.assertRaises(IntegrityError):
            Reparacion.objects.create(numero='REP001', cliente=self.cliente)

    def test_reparacion_public_url_unico(self):
        """
        Verifica que se pueden crear reparaciones con public_url duplicado (no es único).
        """
        Reparacion.objects.create(
            numero='REP001',
            cliente=self.cliente,
            public_url='https://freecom.com/reparacion/rep001'
        )
        # Debería poder crear otra reparación con el mismo public_url
        reparacion2 = Reparacion.objects.create(
            numero='REP002',
            cliente=self.cliente,
            public_url='https://freecom.com/reparacion/rep001'
        )
        self.assertEqual(reparacion2.public_url, 'https://freecom.com/reparacion/rep001')

    def test_reparacion_calculo_total(self):
        """
        Verifica el cálculo automático del total.
        """
        reparacion = Reparacion.objects.create(
            numero='REP001',
            cliente=self.cliente,
            tipo_equipo='Laptop',
            marca='Dell',
            costo_diagnostico=20.00,
            costo_reparacion=100.00,
            costo_repuestos=50.00
        )
        self.assertEqual(float(reparacion.total), 170.00)
        reparacion.costo_repuestos = 75.00
        reparacion.save()
        self.assertEqual(float(reparacion.total), 195.00)  # 20 + 100 + 75

    def test_reparacion_costos_no_negativos(self):
        """
        Verifica que los costos no sean negativos.
        """
        for field, error_msg in [
            ('costo_diagnostico', 'El costo de diagnóstico no puede ser negativo.'),
            ('costo_reparacion', 'El costo de reparación no puede ser negativo.'),
            ('costo_repuestos', 'El costo de repuestos no puede ser negativo.')
        ]:
            with self.assertRaisesMessage(ValidationError, error_msg):
                reparacion = Reparacion(
                    numero='REP001',
                    cliente=self.cliente,
                    tipo_equipo='Laptop',
                    marca='Dell',
                    **{field: -20.00}
                )
                reparacion.full_clean()

    def test_reparacion_fechas_validas(self):
        """
        Verifica que las fechas sean válidas.
        """
        with self.assertRaisesMessage(ValidationError, 'La fecha estimada de entrega no puede ser anterior a la fecha de recepción.'):
            reparacion = Reparacion(
                numero='REP001',
                cliente=self.cliente,
                tipo_equipo='Laptop',
                marca='Dell',
                fecha_recepcion=timezone.now(),
                fecha_estimada_entrega=date.today() - timedelta(days=1)
            )
            reparacion.full_clean()

        with self.assertRaisesMessage(ValidationError, 'La fecha de entrega no puede ser anterior a la fecha de recepción.'):
            reparacion = Reparacion(
                numero='REP002',
                cliente=self.cliente,
                tipo_equipo='Laptop',
                marca='Dell',
                fecha_recepcion=timezone.now(),
                fecha_entrega=timezone.now() - timedelta(days=1)
            )
            reparacion.full_clean()

    def test_reparacion_relaciones(self):
        """
        Verifica las relaciones con Cliente, Técnico y Factura.
        """
        # Crear una venta con detalles
        venta = Venta.objects.create(
            numero='VTA001',
            cliente=self.cliente,
            tipo='factura',
            estado='emitida'
        )
        DetalleVenta.objects.create(
            venta=venta,
            producto=self.producto,
            cantidad=1.00,
            precio_unitario=150.00,
            iva=18.00,
            subtotal=150.00,
            total=168.00
        )
        venta.save()  # Sincronizar totales
        
        reparacion = Reparacion.objects.create(
            numero='REP001',
            cliente=self.cliente,
            tipo_equipo='Laptop',
            marca='Dell',
            tecnico=self.tecnico,
            factura=venta
        )
        self.assertEqual(reparacion.cliente, self.cliente)
        self.assertEqual(reparacion.tecnico, self.tecnico)
        self.assertEqual(reparacion.factura, venta)
        self.assertIn(reparacion, self.cliente.reparaciones.all())
        self.assertIn(reparacion, self.tecnico.reparaciones_asignadas.all())
        self.assertIn(reparacion, venta.reparaciones.all())


class SeguimientoReparacionModelTest(TestCase):
    """
    Pruebas para el modelo SeguimientoReparacion.
    """
    def setUp(self):
        self.cliente = Cliente.objects.create(
            tipo_identificacion='cedula',
            identificacion='1234567890',
            nombres='Juan',
            apellidos='Perez',
            tipo_cliente='persona'
        )
        self.reparacion = Reparacion.objects.create(
            numero='REP001',
            cliente=self.cliente,
            tipo_equipo='Laptop',
            marca='Dell'
        )

    def test_seguimiento_creacion(self):
        """
        Verifica la creación de un seguimiento de reparación.
        """
        seguimiento = SeguimientoReparacion.objects.create(
            reparacion=self.reparacion,
            estado_anterior='recibido',
            estado_nuevo='diagnostico',
            comentario='Iniciando diagnóstico',
            notificado_cliente=True,
            fecha_notificacion=timezone.now(),
            metodo_notificacion='email'
        )
        self.assertEqual(seguimiento.reparacion, self.reparacion)
        self.assertEqual(seguimiento.estado_anterior, 'recibido')
        self.assertEqual(seguimiento.estado_nuevo, 'diagnostico')
        self.assertEqual(seguimiento.comentario, 'Iniciando diagnóstico')
        self.assertTrue(seguimiento.notificado_cliente)
        self.assertIsNotNone(seguimiento.fecha_notificacion)
        self.assertEqual(seguimiento.metodo_notificacion, 'email')
        self.assertIsNotNone(seguimiento.fecha)
        self.assertTrue(isinstance(seguimiento, SeguimientoReparacion))

    def test_seguimiento_str(self):
        """
        Verifica el método __str__ de SeguimientoReparacion.
        """
        seguimiento = SeguimientoReparacion.objects.create(
            reparacion=self.reparacion,
            estado_nuevo='diagnostico',
            comentario='Iniciando diagnóstico'
        )
        self.assertEqual(str(seguimiento), f"{self.reparacion} - {seguimiento.fecha} - diagnostico")

    def test_seguimiento_relacion(self):
        """
        Verifica la relación con Reparacion.
        """
        seguimiento = SeguimientoReparacion.objects.create(
            reparacion=self.reparacion,
            estado_nuevo='diagnostico',
            comentario='Iniciando diagnóstico'
        )
        self.assertEqual(seguimiento.reparacion, self.reparacion)
        self.assertIn(seguimiento, self.reparacion.seguimientos.all())

    def test_seguimiento_estado_nuevo_valido(self):
        """
        Verifica que el estado_nuevo sea válido según ESTADO_CHOICES de Reparacion.
        """
        with self.assertRaisesMessage(ValidationError, 'Estado no válido para la reparación.'):
            seguimiento = SeguimientoReparacion(
                reparacion=self.reparacion,
                estado_nuevo='invalido',
                comentario='Estado no válido'
            )
            seguimiento.full_clean()

    def test_seguimiento_metodo_notificacion(self):
        """
        Verifica el campo metodo_notificacion.
        """
        seguimiento = SeguimientoReparacion.objects.create(
            reparacion=self.reparacion,
            estado_nuevo='diagnostico',
            comentario='Iniciando diagnóstico',
            metodo_notificacion='sms'
        )
        self.assertEqual(seguimiento.metodo_notificacion, 'sms')


class ServicioReparacionModelTest(TestCase):
    """
    Pruebas para el modelo ServicioReparacion.
    """
    def setUp(self):
        self.categoria = Categoria.objects.create(nombre='Electrónica')
        self.cliente = Cliente.objects.create(
            tipo_identificacion='cedula',
            identificacion='1234567890',
            nombres='Juan',
            apellidos='Perez',
            tipo_cliente='persona'
        )
        self.reparacion = Reparacion.objects.create(
            numero='REP001',
            cliente=self.cliente,
            tipo_equipo='Laptop',
            marca='Dell'
        )
        self.producto = Producto.objects.create(
            codigo='SERV001',
            nombre='Diagnóstico de Laptop',
            categoria=self.categoria,
            precio_venta=20.00,
            tipo='servicio',
            es_inventariable=False
        )

    def test_servicio_creacion(self):
        """
        Verifica la creación de un servicio de reparación.
        """
        servicio = ServicioReparacion.objects.create(
            nombre='Diagnóstico de Laptop',
            descripcion='Diagnóstico completo de hardware y software',
            tipo='diagnostico',
            precio=20.00,
            tiempo_estimado=2,
            producto=self.producto,
            requiere_diagnostico_previo=False,
            disponible_online=True
        )
        servicio.reparaciones.add(self.reparacion)
        self.assertEqual(servicio.nombre, 'Diagnóstico de Laptop')
        self.assertEqual(servicio.descripcion, 'Diagnóstico completo de hardware y software')
        self.assertEqual(servicio.tipo, 'diagnostico')
        self.assertEqual(float(servicio.precio), 20.00)
        self.assertEqual(servicio.tiempo_estimado, 2)
        self.assertEqual(servicio.producto, self.producto)
        self.assertFalse(servicio.requiere_diagnostico_previo)
        self.assertTrue(servicio.disponible_online)
        self.assertIn(self.reparacion, servicio.reparaciones.all())
        self.assertTrue(isinstance(servicio, ServicioReparacion))

    def test_servicio_str(self):
        """
        Verifica el método __str__ de ServicioReparacion.
        """
        servicio = ServicioReparacion.objects.create(
            nombre='Diagnóstico de Laptop',
            producto=self.producto,
            precio=20.00
        )
        self.assertEqual(str(servicio), 'Diagnóstico de Laptop')

    def test_servicio_relacion_producto(self):
        """
        Verifica la relación OneToOne con Producto.
        """
        servicio = ServicioReparacion.objects.create(
            nombre='Diagnóstico de Laptop',
            producto=self.producto,
            precio=20.00
        )
        self.assertEqual(servicio.producto, self.producto)
        self.assertEqual(self.producto.servicio_reparacion, servicio)
        self.assertEqual(float(self.producto.precio_venta), 20.00)  # Sincronización de precio

    def test_servicio_precio_no_negativo(self):
        """
        Verifica que el precio no sea negativo.
        """
        with self.assertRaisesMessage(ValidationError, 'El precio no puede ser negativo.'):
            servicio = ServicioReparacion(
                nombre='Diagnóstico de Laptop',
                producto=self.producto,
                precio=-20.00
            )
            servicio.full_clean()

    def test_servicio_producto_valido(self):
        """
        Verifica que el producto sea de tipo 'servicio' y no inventariable.
        """
        producto_invalido = Producto.objects.create(
            codigo='PROD001',
            nombre='Laptop',
            categoria=self.categoria,
            precio_venta=1000.00,
            tipo='producto',
            es_inventariable=True
        )
        with self.assertRaisesMessage(ValidationError, 'El producto asociado debe ser de tipo "servicio".'):
            servicio = ServicioReparacion(
                nombre='Diagnóstico de Laptop',
                producto=producto_invalido,
                precio=20.00
            )
            servicio.full_clean()

        producto_inventariable = Producto.objects.create(
            codigo='SERV002',
            nombre='Otro Servicio',
            categoria=self.categoria,
            precio_venta=20.00,
            tipo='servicio',
            es_inventariable=True
        )
        with self.assertRaisesMessage(ValidationError, 'El producto asociado no debe ser inventariable.'):
            servicio = ServicioReparacion(
                nombre='Otro Servicio',
                producto=producto_inventariable,
                precio=20.00
            )
            servicio.full_clean()

    def test_servicio_relacion_reparaciones(self):
        """
        Verifica la relación ManyToMany con Reparacion.
        """
        servicio = ServicioReparacion.objects.create(
            nombre='Diagnóstico de Laptop',
            producto=self.producto,
            precio=20.00
        )
        servicio.reparaciones.add(self.reparacion)
        self.assertIn(self.reparacion, servicio.reparaciones.all())
        self.assertIn(servicio, self.reparacion.servicios.all())


class RepuestoReparacionModelTest(TestCase):
    """
    Pruebas para el modelo RepuestoReparacion.
    """
    def setUp(self):
        self.cliente = Cliente.objects.create(
            tipo_identificacion='cedula',
            identificacion='1234567890',
            nombres='Juan',
            apellidos='Perez',
            tipo_cliente='persona'
        )
        self.reparacion = Reparacion.objects.create(
            numero='REP001',
            cliente=self.cliente,
            tipo_equipo='Laptop',
            marca='Dell'
        )
        self.categoria = Categoria.objects.create(nombre='Electrónica')
        self.producto = Producto.objects.create(
            codigo='REP001',
            nombre='Pantalla LCD',
            categoria=self.categoria,
            precio_venta=50.00,
            stock=10,
            es_inventariable=True
        )

    def test_repuesto_creacion(self):
        """
        Verifica la creación de un repuesto de reparación.
        """
        repuesto = RepuestoReparacion.objects.create(
            reparacion=self.reparacion,
            producto=self.producto,
            cantidad=2.00,
            precio_unitario=50.00
        )
        self.assertEqual(repuesto.reparacion, self.reparacion)
        self.assertEqual(repuesto.producto, self.producto)
        self.assertEqual(float(repuesto.cantidad), 2.00)
        self.assertEqual(float(repuesto.precio_unitario), 50.00)
        self.assertEqual(float(repuesto.subtotal), 100.00)  # 2 * 50
        self.assertTrue(isinstance(repuesto, RepuestoReparacion))

    def test_repuesto_str(self):
        """
        Verifica el método __str__ de RepuestoReparacion.
        """
        repuesto = RepuestoReparacion.objects.create(
            reparacion=self.reparacion,
            producto=self.producto,
            cantidad=2.00,
            precio_unitario=50.00
        )
        self.assertEqual(str(repuesto), f"{self.producto} x 2.00 - {self.reparacion}")

    def test_repuesto_calculo_subtotal(self):
        """
        Verifica el cálculo automático del subtotal.
        """
        repuesto = RepuestoReparacion.objects.create(
            reparacion=self.reparacion,
            producto=self.producto,
            cantidad=2.00,
            precio_unitario=50.00
        )
        self.assertEqual(float(repuesto.subtotal), 100.00)
        repuesto.cantidad = 3.00
        repuesto.save()
        self.assertEqual(float(repuesto.subtotal), 150.00)  # 3 * 50

    def test_repuesto_valores_no_negativos(self):
        """
        Verifica que la cantidad y el precio unitario no sean negativos.
        """
        with self.assertRaisesMessage(ValidationError, 'La cantidad no puede ser negativa.'):
            repuesto = RepuestoReparacion(
                reparacion=self.reparacion,
                producto=self.producto,
                cantidad=-2.00,
                precio_unitario=50.00
            )
            repuesto.full_clean()

        with self.assertRaisesMessage(ValidationError, 'El precio unitario no puede ser negativo.'):
            repuesto = RepuestoReparacion(
                reparacion=self.reparacion,
                producto=self.producto,
                cantidad=2.00,
                precio_unitario=-50.00
            )
            repuesto.full_clean()

    def test_repuesto_stock_suficiente(self):
        """
        Verifica que la cantidad no exceda el stock disponible.
        """
        with self.assertRaisesMessage(ValidationError, 'La cantidad solicitada excede el stock disponible.'):
            repuesto = RepuestoReparacion(
                reparacion=self.reparacion,
                producto=self.producto,
                cantidad=15.00,  # Stock es 10
                precio_unitario=50.00
            )
            repuesto.full_clean()

    def test_repuesto_relaciones(self):
        """
        Verifica las relaciones con Reparacion y Producto.
        """
        repuesto = RepuestoReparacion.objects.create(
            reparacion=self.reparacion,
            producto=self.producto,
            cantidad=2.00,
            precio_unitario=50.00
        )
        self.assertEqual(repuesto.reparacion, self.reparacion)
        self.assertEqual(repuesto.producto, self.producto)
        self.assertIn(repuesto, self.reparacion.repuestos.all())
        self.assertIn(repuesto, self.producto.reparaciones.all())

    def test_repuesto_calculo_impuesto_unitario(self):
        """
        Verifica el cálculo automático del impuesto unitario según el tipo_iva del producto.
        """
        # Asegúrate de que el producto tenga tipo_iva asignado
        tipo_iva = self.producto.tipo_iva
        repuesto = RepuestoReparacion.objects.create(
            reparacion=self.reparacion,
            producto=self.producto,
            cantidad=2.00,
            precio_unitario=50.00
        )
        monto_iva, _ = IVAService.calcular_iva(50.00, tipo_iva)
        self.assertEqual(float(repuesto.impuesto_unitario), float(monto_iva))


class GarantiaReparacionModelTest(TestCase):
    """
    Pruebas para el modelo GarantiaReparacion.
    """
    def setUp(self):
        self.cliente = Cliente.objects.create(
            tipo_identificacion='cedula',
            identificacion='1234567890',
            nombres='Juan',
            apellidos='Perez',
            tipo_cliente='persona'
        )
        self.reparacion = Reparacion.objects.create(
            numero='REP001',
            cliente=self.cliente,
            tipo_equipo='Laptop',
            marca='Dell'
        )

    def test_garantia_creacion(self):
        """
        Verifica la creación de una garantía de reparación.
        """
        garantia = GarantiaReparacion.objects.create(
            reparacion=self.reparacion,
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=90),
            condiciones='Garantía de 90 días por defectos de reparación'
        )
        self.assertEqual(garantia.reparacion, self.reparacion)
        self.assertEqual(garantia.fecha_inicio, date.today())
        self.assertEqual(garantia.fecha_fin, date.today() + timedelta(days=90))
        self.assertEqual(garantia.condiciones, 'Garantía de 90 días por defectos de reparación')
        self.assertTrue(isinstance(garantia, GarantiaReparacion))

    def test_garantia_str(self):
        """
        Verifica el método __str__ de GarantiaReparacion.
        """
        garantia = GarantiaReparacion.objects.create(
            reparacion=self.reparacion,
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=90)
        )
        self.assertEqual(str(garantia), f"Garantía {self.reparacion} - {garantia.fecha_fin}")

    def test_garantia_relacion(self):
        """
        Verifica la relación con Reparacion.
        """
        garantia = GarantiaReparacion.objects.create(
            reparacion=self.reparacion,
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=90)
        )
        self.assertEqual(garantia.reparacion, self.reparacion)
        self.assertIn(garantia, self.reparacion.garantias.all())

    def test_garantia_fechas_validas(self):
        """
        Verifica que la fecha_fin no sea anterior a fecha_inicio.
        """
        with self.assertRaises(ValidationError):
            garantia = GarantiaReparacion(
                reparacion=self.reparacion,
                fecha_inicio=date.today(),
                fecha_fin=date.today() - timedelta(days=1),
                condiciones='Garantía inválida'
            )
            garantia.full_clean()


class CitaServicioModelTest(TestCase):
    """
    Pruebas para el modelo CitaServicio.
    """
    def setUp(self):
        self.cliente = Cliente.objects.create(
            tipo_identificacion='cedula',
            identificacion='1234567890',
            nombres='Juan',
            apellidos='Perez',
            tipo_cliente='persona'
        )
        self.reparacion = Reparacion.objects.create(
            numero='REP001',
            cliente=self.cliente,
            tipo_equipo='Laptop',
            marca='Dell'
        )

    def test_cita_creacion(self):
        """
        Verifica la creación de una cita de servicio.
        """
        cita = CitaServicio.objects.create(
            cliente=self.cliente,
            fecha_hora=timezone.now() + timedelta(days=1),
            tipo_equipo='Laptop',
            estado='pendiente',
            reparacion=self.reparacion
        )
        self.assertEqual(cita.cliente, self.cliente)
        self.assertEqual(cita.tipo_equipo, 'Laptop')
        self.assertEqual(cita.estado, 'pendiente')
        self.assertEqual(cita.reparacion, self.reparacion)
        self.assertIsNotNone(cita.fecha_hora)
        self.assertTrue(isinstance(cita, CitaServicio))

    def test_cita_str(self):
        """
        Verifica el método __str__ de CitaServicio.
        """
        cita = CitaServicio.objects.create(
            cliente=self.cliente,
            fecha_hora=timezone.now() + timedelta(days=1),
            tipo_equipo='Laptop'
        )
        self.assertEqual(str(cita), f"Cita {self.cliente} - {cita.fecha_hora}")

    def test_cita_relaciones(self):
        """
        Verifica las relaciones con Cliente y Reparacion.
        """
        cita = CitaServicio.objects.create(
            cliente=self.cliente,
            fecha_hora=timezone.now() + timedelta(days=1),
            tipo_equipo='Laptop',
            reparacion=self.reparacion
        )
        self.assertEqual(cita.cliente, self.cliente)
        self.assertEqual(cita.reparacion, self.reparacion)
        self.assertIn(cita, self.cliente.citas.all())
        self.assertIn(cita, self.reparacion.citas.all())

    def test_cita_fecha_futura(self):
        """
        Verifica que la fecha_hora no sea en el pasado.
        """
        with self.assertRaises(ValidationError):
            cita = CitaServicio(
                cliente=self.cliente,
                fecha_hora=timezone.now() - timedelta(days=1),
                tipo_equipo='Laptop'
            )
            cita.full_clean()