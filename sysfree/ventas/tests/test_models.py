from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.utils import IntegrityError
from datetime import datetime, timedelta
from decimal import Decimal
from ventas.models import Venta, DetalleVenta, Pago, NotaCredito, DetalleNotaCredito, Envio
from clientes.models import Cliente, DireccionCliente
from inventario.models import Producto, Categoria
from reparaciones.models import Reparacion

class VentaModelTest(TestCase):
    """Pruebas para el modelo Venta."""
    
    def setUp(self):
        self.cliente = Cliente.objects.create(
            tipo_identificacion='cedula',
            identificacion='1234567890',
            nombres='Juan',
            apellidos='Perez',
            tipo_cliente='persona'
        )
        self.direccion = DireccionCliente.objects.create(
            cliente=self.cliente,
            direccion='Av. Principal 123',
            tipo='facturacion'
        )
        self.categoria = Categoria.objects.create(nombre='Electrónica')
        self.producto = Producto.objects.create(
            codigo='TV001',
            nombre='Smart TV 55"',
            categoria=self.categoria,
            precio_venta=600.00,
            stock=10.00,
            es_inventariable=True
        )

    def test_venta_creacion(self):
        """Verifica la creación de una venta."""
        venta = Venta.objects.create(
            numero='FAC001',
            cliente=self.cliente,
            direccion_facturacion=self.direccion,
            tipo='factura',
            estado='borrador',
            subtotal=500.00,
            iva=60.00,
            descuento=50.00,
            total=510.00,
            validez=15,
            clave_acceso='1234567890',
            notas='Venta inicial'
        )
        self.assertEqual(venta.numero, 'FAC001')
        self.assertEqual(venta.cliente, self.cliente)
        self.assertEqual(venta.direccion_facturacion, self.direccion)
        self.assertEqual(venta.tipo, 'factura')
        self.assertEqual(venta.estado, 'borrador')
        self.assertEqual(float(venta.subtotal), 500.00)
        self.assertEqual(float(venta.iva), 60.00)
        self.assertEqual(float(venta.descuento), 50.00)
        self.assertEqual(float(venta.total), 510.00)
        self.assertEqual(venta.validez, 15)
        self.assertEqual(venta.clave_acceso, '1234567890')
        self.assertEqual(venta.notas, 'Venta inicial')
        self.assertIsNotNone(venta.fecha)
        self.assertTrue(isinstance(venta, Venta))

    def test_venta_str(self):
        """Verifica el método __str__ de Venta."""
        venta = Venta.objects.create(numero='FAC001', cliente=self.cliente)
        self.assertEqual(str(venta), f"FAC001 - {self.cliente}")

    def test_venta_numero_unico(self):
        """Verifica que el campo numero sea único."""
        Venta.objects.create(numero='FAC001', cliente=self.cliente)
        with self.assertRaises(IntegrityError):
            Venta.objects.create(numero='FAC001', cliente=self.cliente)

    def test_venta_valores_no_negativos(self):
        """Verifica que los valores numéricos no sean negativos."""
        for field, error_msg in [
            ('subtotal', 'El subtotal no puede ser negativo.'),
            ('iva', 'El IVA no puede ser negativo.'),
            ('descuento', 'El descuento no puede ser negativo.'),
            ('total', 'El total no puede ser negativo.')
        ]:
            with self.assertRaisesMessage(ValidationError, error_msg):
                venta = Venta(
                    numero='FAC001',
                    cliente=self.cliente,
                    **{field: -100.00}
                )
                venta.full_clean()

    def test_venta_validez_positiva(self):
        """Verifica que la validez sea positiva."""
        with self.assertRaisesMessage(ValidationError, 'La validez debe ser positiva.'):
            venta = Venta(
                numero='FAC001',
                cliente=self.cliente,
                validez=0
            )
            venta.full_clean()

    def test_venta_proforma_estado_invalido(self):
        """Verifica que las proformas no usen estados inválidos."""
        with self.assertRaisesMessage(ValidationError, 'Las proformas no pueden estar en estado emitida, pagada o anulada.'):
            venta = Venta(
                numero='PROF001',
                cliente=self.cliente,
                tipo='proforma',
                estado='emitida'
            )
            venta.full_clean()

    def test_venta_sincroniza_detalles(self):
        """Verifica que subtotal, IVA, descuento y total se sincronicen con los detalles."""
        venta = Venta.objects.create(numero='FAC001', cliente=self.cliente)
        DetalleVenta.objects.create(
            venta=venta,
            producto=self.producto,
            cantidad=2.00,
            precio_unitario=500.00,
            descuento=50.00,
            iva=60.00
        )
        venta.save()
        venta.refresh_from_db()
        self.assertEqual(float(venta.subtotal), 950.00)  # 2 * 500 - 50
        self.assertEqual(float(venta.iva), 60.00)
        self.assertEqual(float(venta.descuento), 50.00)
        self.assertEqual(float(venta.total), 1010.00)  # 950 + 60

    def test_venta_esta_pagado(self):
        """Verifica la propiedad esta_pagado."""
        venta = Venta.objects.create(
            numero='FAC001',
            cliente=self.cliente,
            total=1000.00
        )
        Pago.objects.create(
            venta=venta,
            metodo='efectivo',
            monto=500.00,
            estado='aprobado'
        )
        self.assertFalse(venta.esta_pagado)
        Pago.objects.create(
            venta=venta,
            metodo='tarjeta',
            monto=500.00,
            estado='aprobado'
        )
        self.assertTrue(venta.esta_pagado)

    def test_venta_esta_vencida(self):
        """Verifica la propiedad esta_vencida."""
        venta = Venta.objects.create(
            numero='PROF001',
            cliente=self.cliente,
            tipo='proforma',
            validez=15
        )
        # Establecer una fecha pasada explícitamente
        venta.fecha = timezone.now() - timedelta(days=20)
        venta.save()
        self.assertTrue(venta.esta_vencida)
        
        venta_proforma_no_vencida = Venta.objects.create(
            numero='PROF002',
            cliente=self.cliente,
            tipo='proforma',
            validez=15
        )
        self.assertFalse(venta_proforma_no_vencida.esta_vencida)
        
        venta_factura = Venta.objects.create(
            numero='FAC002',
            cliente=self.cliente,
            tipo='factura'
        )
        self.assertFalse(venta_factura.esta_vencida)

class DetalleVentaModelTest(TestCase):
    """Pruebas para el modelo DetalleVenta."""
    
    def setUp(self):
        self.cliente = Cliente.objects.create(
            tipo_identificacion='cedula',
            identificacion='1234567890',
            nombres='Juan',
            apellidos='Perez',
            tipo_cliente='persona'
        )
        self.categoria = Categoria.objects.create(nombre='Electrónica')
        self.producto = Producto.objects.create(
            codigo='TV001',
            nombre='Smart TV 55"',
            categoria=self.categoria,
            precio_venta=600.00,
            stock=10.00,
            es_inventariable=True
        )
        self.venta = Venta.objects.create(numero='FAC001', cliente=self.cliente)

    def test_detalle_venta_creacion(self):
        """Verifica la creación de un detalle de venta."""
        detalle = DetalleVenta.objects.create(
            venta=self.venta,
            producto=self.producto,
            cantidad=2.00,
            precio_unitario=500.00,
            descuento=50.00,
            iva=60.00
        )
        self.assertEqual(detalle.venta, self.venta)
        self.assertEqual(detalle.producto, self.producto)
        self.assertEqual(float(detalle.cantidad), 2.00)
        self.assertEqual(float(detalle.precio_unitario), 500.00)
        self.assertEqual(float(detalle.descuento), 50.00)
        self.assertEqual(float(detalle.iva), 60.00)
        self.assertEqual(float(detalle.subtotal), 950.00)  # 2 * 500 - 50
        self.assertEqual(float(detalle.total), 1010.00)  # 950 + 60
        self.assertTrue(isinstance(detalle, DetalleVenta))

    def test_detalle_venta_str(self):
        """Verifica el método __str__ de DetalleVenta."""
        detalle = DetalleVenta.objects.create(
            venta=self.venta,
            producto=self.producto,
            cantidad=2.00,
            precio_unitario=500.00
        )
        self.assertEqual(str(detalle), f"{self.producto} x 2.00")

    def test_detalle_venta_valores_no_negativos(self):
        """Verifica que los valores numéricos no sean negativos."""
        for field, error_msg in [
            ('cantidad', 'La cantidad debe ser positiva.'),
            ('precio_unitario', 'El precio unitario no puede ser negativo.'),
            ('descuento', 'El descuento no puede ser negativo.'),
            ('iva', 'El IVA no puede ser negativo.')
        ]:
            kwargs = {
                'venta': self.venta,
                'producto': self.producto,
                'cantidad': 2.00,
                'precio_unitario': 500.00
            }
            kwargs[field] = -1.00 if field != 'cantidad' else 0.00
            with self.assertRaisesMessage(ValidationError, error_msg):
                detalle = DetalleVenta(**kwargs)
                detalle.full_clean()

    def test_detalle_venta_stock_suficiente(self):
        """Verifica que la cantidad no exceda el stock disponible."""
        with self.assertRaisesMessage(ValidationError, 'La cantidad solicitada excede el stock disponible.'):
            detalle = DetalleVenta(
                venta=self.venta,
                producto=self.producto,
                cantidad=15.00,  # Stock es 10
                precio_unitario=500.00
            )
            detalle.full_clean()

    def test_detalle_venta_actualiza_stock(self):
        """Verifica que el stock del producto se actualice."""
        self.venta.estado = 'emitida'
        self.venta.save()
        detalle = DetalleVenta.objects.create(
            venta=self.venta,
            producto=self.producto,
            cantidad=3.00,
            precio_unitario=500.00
        )
        self.producto.refresh_from_db()
        self.assertEqual(float(self.producto.stock), 7.00)  # 10 - 3

class PagoModelTest(TestCase):
    """Pruebas para el modelo Pago."""
    
    def setUp(self):
        self.cliente = Cliente.objects.create(
            tipo_identificacion='cedula',
            identificacion='1234567890',
            nombres='Juan',
            apellidos='Perez',
            tipo_cliente='persona'
        )
        self.venta = Venta.objects.create(numero='FAC001', cliente=self.cliente)

    def test_pago_creacion(self):
        """Verifica la creación de un pago."""
        pago = Pago.objects.create(
            venta=self.venta,
            metodo='tarjeta',
            monto=500.00,
            referencia='TX123',
            estado='aprobado',
            numero_tarjeta='1234567890123456',
            titular_tarjeta='Juan Perez',
            notas='Pago inicial'
        )
        self.assertEqual(pago.venta, self.venta)
        self.assertEqual(pago.metodo, 'tarjeta')
        self.assertEqual(float(pago.monto), 500.00)
        self.assertEqual(pago.referencia, 'TX123')
        self.assertEqual(pago.estado, 'aprobado')
        self.assertEqual(pago.numero_tarjeta, '1234567890123456')
        self.assertEqual(pago.titular_tarjeta, 'Juan Perez')
        self.assertEqual(pago.notas, 'Pago inicial')
        self.assertIsNotNone(pago.fecha)
        self.assertTrue(isinstance(pago, Pago))

    def test_pago_str(self):
        """Verifica el método __str__ de Pago."""
        pago = Pago.objects.create(
            venta=self.venta,
            metodo='efectivo',
            monto=500.00
        )
        self.assertEqual(str(pago), f"Efectivo - 500.00")

    def test_pago_monto_positivo(self):
        """Verifica que el monto sea positivo."""
        with self.assertRaisesMessage(ValidationError, 'El monto debe ser positivo.'):
            pago = Pago(
                venta=self.venta,
                metodo='efectivo',
                monto=0.00
            )
            pago.full_clean()

    def test_pago_campos_tarjeta_requeridos(self):
        """Verifica que los campos de tarjeta sean requeridos."""
        with self.assertRaisesMessage(ValidationError, 'El número y titular de la tarjeta son requeridos para pagos con tarjeta.'):
            pago = Pago(
                venta=self.venta,
                metodo='tarjeta',
                monto=500.00
            )
            pago.full_clean()

    def test_pago_campos_transferencia_requeridos(self):
        """Verifica que los campos de transferencia sean requeridos."""
        with self.assertRaisesMessage(ValidationError, 'El banco y número de cuenta son requeridos para transferencias.'):
            pago = Pago(
                venta=self.venta,
                metodo='transferencia',
                monto=500.00
            )
            pago.full_clean()

    def test_pago_campos_cheque_requeridos(self):
        """Verifica que los campos de cheque sean requeridos."""
        with self.assertRaisesMessage(ValidationError, 'El número y banco del cheque son requeridos para pagos con cheque.'):
            pago = Pago(
                venta=self.venta,
                metodo='cheque',
                monto=500.00
            )
            pago.full_clean()

class NotaCreditoModelTest(TestCase):
    """Pruebas para el modelo NotaCredito."""
    
    def setUp(self):
        self.cliente = Cliente.objects.create(
            tipo_identificacion='cedula',
            identificacion='1234567890',
            nombres='Juan',
            apellidos='Perez',
            tipo_cliente='persona'
        )
        self.categoria = Categoria.objects.create(nombre='Electrónica')
        self.producto = Producto.objects.create(
            codigo='TV001',
            nombre='Smart TV 55"',
            categoria=self.categoria,
            precio_venta=600.00,
            stock=10.00,
            es_inventariable=True
        )
        self.venta = Venta.objects.create(numero='FAC001', cliente=self.cliente)

    def test_nota_credito_creacion(self):
        """Verifica la creación de una nota de crédito."""
        nota = NotaCredito.objects.create(
            numero='NC001',
            venta=self.venta,
            cliente=self.cliente,
            motivo='Devolución por defecto',
            subtotal=500.00,
            iva=60.00,
            total=560.00,
            estado='borrador'
        )
        self.assertEqual(nota.numero, 'NC001')
        self.assertEqual(nota.venta, self.venta)
        self.assertEqual(nota.cliente, self.cliente)
        self.assertEqual(nota.motivo, 'Devolución por defecto')
        self.assertEqual(float(nota.subtotal), 500.00)
        self.assertEqual(float(nota.iva), 60.00)
        self.assertEqual(float(nota.total), 560.00)
        self.assertEqual(nota.estado, 'borrador')
        self.assertIsNotNone(nota.fecha)
        self.assertTrue(isinstance(nota, NotaCredito))

    def test_nota_credito_str(self):
        """Verifica el método __str__ de NotaCredito."""
        nota = NotaCredito.objects.create(numero='NC001', venta=self.venta, cliente=self.cliente)
        self.assertEqual(str(nota), f"NC001 - {self.cliente}")

    def test_nota_credito_numero_unico(self):
        """Verifica que el campo numero sea único."""
        NotaCredito.objects.create(numero='NC001', venta=self.venta, cliente=self.cliente)
        with self.assertRaises(IntegrityError):
            NotaCredito.objects.create(numero='NC001', venta=self.venta, cliente=self.cliente)

    def test_nota_credito_valores_no_negativos(self):
        """Verifica que los valores numéricos no sean negativos."""
        for field, error_msg in [
            ('subtotal', 'El subtotal no puede ser negativo.'),
            ('iva', 'El IVA no puede ser negativo.'),
            ('total', 'El total no puede ser negativo.')
        ]:
            with self.assertRaisesMessage(ValidationError, error_msg):
                nota = NotaCredito(
                    numero='NC001',
                    venta=self.venta,
                    cliente=self.cliente,
                    **{field: -100.00}
                )
                nota.full_clean()

    def test_nota_credito_sincroniza_detalles(self):
        """Verifica que subtotal, IVA y total se sincronicen con los detalles."""
        nota = NotaCredito.objects.create(numero='NC001', venta=self.venta, cliente=self.cliente)
        DetalleNotaCredito.objects.create(
            nota_credito=nota,
            producto=self.producto,
            cantidad=2.00,
            precio_unitario=500.00,
            iva=60.00
        )
        nota.save()
        nota.refresh_from_db()
        self.assertEqual(float(nota.subtotal), 1000.00)  # 2 * 500
        self.assertEqual(float(nota.iva), 60.00)
        self.assertEqual(float(nota.total), 1060.00)  # 1000 + 60

class DetalleNotaCreditoModelTest(TestCase):
    """Pruebas para el modelo DetalleNotaCredito."""
    
    def setUp(self):
        self.cliente = Cliente.objects.create(
            tipo_identificacion='cedula',
            identificacion='1234567890',
            nombres='Juan',
            apellidos='Perez',
            tipo_cliente='persona'
        )
        self.categoria = Categoria.objects.create(nombre='Electrónica')
        self.producto = Producto.objects.create(
            codigo='TV001',
            nombre='Smart TV 55"',
            categoria=self.categoria,
            precio_venta=600.00,
            stock=10.00,
            es_inventariable=True
        )
        self.venta = Venta.objects.create(numero='FAC001', cliente=self.cliente)
        self.nota = NotaCredito.objects.create(numero='NC001', venta=self.venta, cliente=self.cliente)

    def test_detalle_nota_credito_creacion(self):
        """Verifica la creación de un detalle de nota de crédito."""
        detalle = DetalleNotaCredito.objects.create(
            nota_credito=self.nota,
            producto=self.producto,
            cantidad=2.00,
            precio_unitario=500.00,
            iva=60.00
        )
        self.assertEqual(detalle.nota_credito, self.nota)
        self.assertEqual(detalle.producto, self.producto)
        self.assertEqual(float(detalle.cantidad), 2.00)
        self.assertEqual(float(detalle.precio_unitario), 500.00)
        self.assertEqual(float(detalle.iva), 60.00)
        self.assertEqual(float(detalle.subtotal), 1000.00)  # 2 * 500
        self.assertEqual(float(detalle.total), 1060.00)  # 1000 + 60
        self.assertTrue(isinstance(detalle, DetalleNotaCredito))

    def test_detalle_nota_credito_str(self):
        """Verifica el método __str__ de DetalleNotaCredito."""
        detalle = DetalleNotaCredito.objects.create(
            nota_credito=self.nota,
            producto=self.producto,
            cantidad=2.00,
            precio_unitario=500.00
        )
        self.assertEqual(str(detalle), f"{self.producto} x 2.00")

    def test_detalle_nota_credito_valores_no_negativos(self):
        """Verifica que los valores numéricos no sean negativos."""
        for field, error_msg in [
            ('cantidad', 'La cantidad debe ser positiva.'),
            ('precio_unitario', 'El precio unitario no puede ser negativo.'),
            ('iva', 'El IVA no puede ser negativo.')
        ]:
            kwargs = {
                'nota_credito': self.nota,
                'producto': self.producto,
                'cantidad': 2.00,
                'precio_unitario': 500.00
            }
            kwargs[field] = -1.00 if field != 'cantidad' else 0.00
            with self.assertRaisesMessage(ValidationError, error_msg):
                detalle = DetalleNotaCredito(**kwargs)
                detalle.full_clean()

    def test_detalle_nota_credito_actualiza_stock(self):
        """Verifica que el stock del producto se actualice."""
        self.nota.estado = 'emitida'
        self.nota.save()
        detalle = DetalleNotaCredito.objects.create(
            nota_credito=self.nota,
            producto=self.producto,
            cantidad=3.00,
            precio_unitario=500.00
        )
        self.producto.refresh_from_db()
        self.assertEqual(float(self.producto.stock), 13.00)  # 10 + 3

class EnvioModelTest(TestCase):
    """Pruebas para el modelo Envio."""
    
    def setUp(self):
        self.cliente = Cliente.objects.create(
            tipo_identificacion='cedula',
            identificacion='1234567890',
            nombres='Juan',
            apellidos='Perez',
            tipo_cliente='persona'
        )
        self.venta = Venta.objects.create(numero='FAC001', cliente=self.cliente)

    def test_envio_creacion(self):
        """Verifica la creación de un envío."""
        envio = Envio.objects.create(
            venta=self.venta,
            transportista='FedEx',
            numero_seguimiento='1234567890',
            fecha_envio=timezone.now(),
            estado='en_transito',
            notas='Envío urgente'
        )
        self.assertEqual(envio.venta, self.venta)
        self.assertEqual(envio.transportista, 'FedEx')
        self.assertEqual(envio.numero_seguimiento, '1234567890')
        self.assertEqual(envio.estado, 'en_transito')
        self.assertEqual(envio.notas, 'Envío urgente')
        self.assertIsNotNone(envio.fecha_envio)
        self.assertTrue(isinstance(envio, Envio))

    def test_envio_str(self):
        """Verifica el método __str__ de Envio."""
        envio = Envio.objects.create(venta=self.venta, transportista='FedEx')
        self.assertEqual(str(envio), f"Envío FAC001 - FedEx")

    def test_envio_fechas_validas(self):
        """Verifica que la fecha de entrega no sea anterior a la fecha de envío."""
        with self.assertRaisesMessage(ValidationError, 'La fecha de entrega no puede ser anterior a la fecha de envío.'):
            envio = Envio(
                venta=self.venta,
                transportista='FedEx',
                fecha_envio=timezone.now(),
                fecha_entrega=timezone.now() - timedelta(days=1)
            )
            envio.full_clean()