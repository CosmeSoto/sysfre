from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.utils import IntegrityError
from datetime import date, timedelta
from django.db import models

from fiscal.models import (
    AsientoContable, Comprobante, CuentaContable, Impuesto,
    LineaAsiento, PeriodoFiscal
)
from core.models import ModeloBase
from inventario.models import Proveedor

class ModeloBaseTest(TestCase):
    """
    Pruebas para el modelo abstracto ModeloBase.
    """
    def test_modelo_base_atributos(self):
        """
        Verifica que los atributos de ModeloBase se establezcan correctamente.
        """
        impuesto = Impuesto.objects.create(
            nombre="Test",
            codigo="TEST",
            porcentaje=0.00
        )
        self.assertIsNotNone(impuesto.fecha_creacion)
        self.assertIsNotNone(impuesto.fecha_modificacion)
        self.assertIsNone(impuesto.creado_por)
        self.assertIsNone(impuesto.modificado_por)
        self.assertTrue(impuesto.activo)


class ImpuestoModelTest(TestCase):
    """
    Pruebas para el modelo Impuesto.
    """
    def test_impuesto_creacion(self):
        """
        Verifica la creación de un impuesto.
        """
        impuesto = Impuesto.objects.create(
            nombre="IVA",
            codigo="IVA12",
            porcentaje=12.00,
            descripcion="Impuesto al Valor Agregado 12%"
        )
        self.assertEqual(impuesto.nombre, "IVA")
        self.assertEqual(impuesto.codigo, "IVA12")
        self.assertEqual(float(impuesto.porcentaje), 12.00)
        self.assertEqual(impuesto.descripcion, "Impuesto al Valor Agregado 12%")
        self.assertTrue(isinstance(impuesto, Impuesto))

    def test_impuesto_str(self):
        """
        Verifica el método __str__ de Impuesto.
        """
        impuesto = Impuesto.objects.create(
            nombre="IVA",
            codigo="IVA12",
            porcentaje=12.00
        )
        self.assertEqual(str(impuesto), "IVA (12.00%)")

    def test_impuesto_codigo_unico(self):
        """
        Verifica que el campo codigo sea único.
        """
        Impuesto.objects.create(nombre="IVA", codigo="IVA12", porcentaje=12.00)
        with self.assertRaises(IntegrityError):
            Impuesto.objects.create(nombre="VAT", codigo="IVA12", porcentaje=10.00)

    def test_impuesto_porcentaje_negativo(self):
        """
        Verifica que no se permita un porcentaje negativo.
        """
        with self.assertRaises(ValidationError):
            impuesto = Impuesto(
                nombre="IVA Negativo",
                codigo="IVANEG",
                porcentaje=-5.00
            )
            impuesto.full_clean()


class PeriodoFiscalModelTest(TestCase):
    """
    Pruebas para el modelo PeriodoFiscal.
    """
    def test_periodo_fiscal_creacion(self):
        """
        Verifica la creación de un periodo fiscal.
        """
        start_date = date(2023, 1, 1)
        end_date = date(2023, 12, 31)
        periodo = PeriodoFiscal.objects.create(
            nombre="2023",
            fecha_inicio=start_date,
            fecha_fin=end_date,
            estado='abierto',
            notas="Periodo fiscal del año 2023"
        )
        self.assertEqual(periodo.nombre, "2023")
        self.assertEqual(periodo.fecha_inicio, start_date)
        self.assertEqual(periodo.fecha_fin, end_date)
        self.assertEqual(periodo.estado, 'abierto')
        self.assertEqual(periodo.notas, "Periodo fiscal del año 2023")
        self.assertTrue(isinstance(periodo, PeriodoFiscal))

    def test_periodo_fiscal_str(self):
        """
        Verifica el método __str__ de PeriodoFiscal.
        """
        start_date = date(2023, 1, 1)
        end_date = date(2023, 12, 31)
        periodo = PeriodoFiscal.objects.create(
            nombre="2023",
            fecha_inicio=start_date,
            fecha_fin=end_date
        )
        self.assertEqual(str(periodo), "2023")

    def test_periodo_fiscal_esta_activo(self):
        """
        Verifica la propiedad esta_activo de PeriodoFiscal.
        """
        today = timezone.now().date()
        active_start = today - timedelta(days=10)
        active_end = today + timedelta(days=10)
        active_periodo = PeriodoFiscal.objects.create(
            nombre="Activo",
            fecha_inicio=active_start,
            fecha_fin=active_end,
            estado='abierto'
        )
        self.assertTrue(active_periodo.esta_activo)

        closed_periodo = PeriodoFiscal.objects.create(
            nombre="Cerrado",
            fecha_inicio=active_start,
            fecha_fin=active_end,
            estado='cerrado'
        )
        self.assertFalse(closed_periodo.esta_activo)

        past_end = today - timedelta(days=1)
        past_periodo = PeriodoFiscal.objects.create(
            nombre="Pasado",
            fecha_inicio=active_start - timedelta(days=30),
            fecha_fin=past_end,
            estado='abierto'
        )
        self.assertFalse(past_periodo.esta_activo)

        future_start = today + timedelta(days=1)
        future_periodo = PeriodoFiscal.objects.create(
            nombre="Futuro",
            fecha_inicio=future_start,
            fecha_fin=future_start + timedelta(days=30),
            estado='abierto'
        )
        self.assertFalse(future_periodo.esta_activo)

    def test_periodo_fiscal_fecha_invalida(self):
        """
        Verifica que la fecha de fin no sea anterior a la fecha de inicio.
        """
        with self.assertRaises(ValidationError):
            periodo = PeriodoFiscal(
                nombre="Inválido",
                fecha_inicio=date(2023, 12, 31),
                fecha_fin=date(2023, 1, 1),
                estado='abierto'
            )
            periodo.full_clean()


class CuentaContableModelTest(TestCase):
    """
    Pruebas para el modelo CuentaContable.
    """
    def test_cuenta_contable_creacion(self):
        """
        Verifica la creación de una cuenta contable.
        """
        cuenta = CuentaContable.objects.create(
            codigo="101",
            nombre="Caja",
            tipo="activo",
            descripcion="Efectivo en caja chica"
        )
        self.assertEqual(cuenta.codigo, "101")
        self.assertEqual(cuenta.nombre, "Caja")
        self.assertEqual(cuenta.tipo, "activo")
        self.assertIsNone(cuenta.cuenta_padre)
        self.assertEqual(cuenta.descripcion, "Efectivo en caja chica")
        self.assertTrue(isinstance(cuenta, CuentaContable))

    def test_cuenta_contable_str(self):
        """
        Verifica el método __str__ de CuentaContable.
        """
        cuenta = CuentaContable.objects.create(codigo="101", nombre="Caja", tipo="activo")
        self.assertEqual(str(cuenta), "101 - Caja")

    def test_cuenta_contable_codigo_unico(self):
        """
        Verifica que el campo codigo sea único.
        """
        CuentaContable.objects.create(codigo="101", nombre="Caja", tipo="activo")
        with self.assertRaises(IntegrityError):
            CuentaContable.objects.create(codigo="101", nombre="Bancos", tipo="activo")

    def test_cuenta_contable_relacion_padre(self):
        """
        Verifica la relación padre-hijo de CuentaContable.
        """
        parent_cuenta = CuentaContable.objects.create(codigo="100", nombre="Activos", tipo="activo")
        child_cuenta = CuentaContable.objects.create(
            codigo="101",
            nombre="Caja",
            tipo="activo",
            cuenta_padre=parent_cuenta
        )
        self.assertEqual(child_cuenta.cuenta_padre, parent_cuenta)
        self.assertIn(child_cuenta, parent_cuenta.subcuentas.all())

    def test_cuenta_contable_ruta_completa(self):
        """
        Verifica la propiedad ruta_completa de CuentaContable.
        """
        parent1 = CuentaContable.objects.create(codigo="100", nombre="Activos", tipo="activo")
        parent2 = CuentaContable.objects.create(
            codigo="110",
            nombre="Activos Corrientes",
            tipo="activo",
            cuenta_padre=parent1
        )
        child = CuentaContable.objects.create(
            codigo="111",
            nombre="Caja",
            tipo="activo",
            cuenta_padre=parent2
        )
        self.assertEqual(parent1.ruta_completa, "Activos")
        self.assertEqual(parent2.ruta_completa, "Activos > Activos Corrientes")
        self.assertEqual(child.ruta_completa, "Activos > Activos Corrientes > Caja")


class AsientoContableModelTest(TestCase):
    """
    Pruebas para el modelo AsientoContable.
    """
    def setUp(self):
        self.periodo = PeriodoFiscal.objects.create(
            nombre="2023",
            fecha_inicio=date(2023, 1, 1),
            fecha_fin=date(2023, 12, 31),
            estado='abierto'
        )

    def test_asiento_contable_creacion(self):
        """
        Verifica la creación de un asiento contable.
        """
        asiento = AsientoContable.objects.create(
            numero="001",
            fecha=date(2023, 10, 26),
            periodo_fiscal=self.periodo,
            tipo='manual',
            concepto="Registro de gastos",
            estado='borrador',
            notas="Notas del asiento"
        )
        self.assertEqual(asiento.numero, "001")
        self.assertEqual(asiento.fecha, date(2023, 10, 26))
        self.assertEqual(asiento.periodo_fiscal, self.periodo)
        self.assertEqual(asiento.tipo, 'manual')
        self.assertEqual(asiento.concepto, "Registro de gastos")
        self.assertEqual(asiento.estado, 'borrador')
        self.assertEqual(asiento.notas, "Notas del asiento")
        self.assertIsNone(asiento.referencia_id)
        self.assertEqual(asiento.referencia_tipo, "")
        self.assertTrue(isinstance(asiento, AsientoContable))

    def test_asiento_contable_str(self):
        """
        Verifica el método __str__ de AsientoContable.
        """
        asiento = AsientoContable.objects.create(
            numero="001",
            fecha=date(2023, 10, 26),
            periodo_fiscal=self.periodo,
            concepto="Registro de gastos"
        )
        self.assertEqual(str(asiento), "001 - Registro de gastos")

    def test_asiento_contable_numero_unico(self):
        """
        Verifica que el campo numero sea único.
        """
        AsientoContable.objects.create(
            numero="001",
            fecha=date(2023, 10, 26),
            periodo_fiscal=self.periodo,
            concepto="Asiento 1"
        )
        with self.assertRaises(IntegrityError):
            AsientoContable.objects.create(
                numero="001",
                fecha=date(2023, 10, 27),
                periodo_fiscal=self.periodo,
                concepto="Asiento 2"
            )

    def test_asiento_contable_total_debe_haber(self):
        """
        Verifica las propiedades total_debe y total_haber de AsientoContable.
        """
        asiento = AsientoContable.objects.create(
            numero="002",
            fecha=date(2023, 10, 26),
            periodo_fiscal=self.periodo,
            concepto="Asiento con líneas"
        )
        cuenta_debe = CuentaContable.objects.create(codigo="101", nombre="Caja", tipo="activo")
        cuenta_haber = CuentaContable.objects.create(codigo="401", nombre="Ventas", tipo="ingreso")

        LineaAsiento.objects.create(asiento=asiento, cuenta=cuenta_debe, debe=100.00)
        LineaAsiento.objects.create(asiento=asiento, cuenta=cuenta_haber, haber=100.00)

        self.assertEqual(float(asiento.total_debe), 100.00)
        self.assertEqual(float(asiento.total_haber), 100.00)

    def test_asiento_contable_esta_balanceado(self):
        """
        Verifica la propiedad esta_balanceado de AsientoContable.
        """
        asiento_balanceado = AsientoContable.objects.create(
            numero="003",
            fecha=date(2023, 10, 26),
            periodo_fiscal=self.periodo,
            concepto="Asiento balanceado"
        )
        cuenta1 = CuentaContable.objects.create(codigo="101", nombre="Caja", tipo="activo")
        cuenta2 = CuentaContable.objects.create(codigo="401", nombre="Ventas", tipo="ingreso")
        LineaAsiento.objects.create(asiento=asiento_balanceado, cuenta=cuenta1, debe=250.00)
        LineaAsiento.objects.create(asiento=asiento_balanceado, cuenta=cuenta2, haber=250.00)
        self.assertTrue(asiento_balanceado.esta_balanceado)

        asiento_desbalanceado = AsientoContable.objects.create(
            numero="004",
            fecha=date(2023, 10, 26),
            periodo_fiscal=self.periodo,
            concepto="Asiento desbalanceado"
        )
        LineaAsiento.objects.create(asiento=asiento_desbalanceado, cuenta=cuenta1, debe=100.00)
        LineaAsiento.objects.create(asiento=asiento_desbalanceado, cuenta=cuenta2, haber=150.00)
        self.assertFalse(asiento_desbalanceado.esta_balanceado)


class LineaAsientoModelTest(TestCase):
    """
    Pruebas para el modelo LineaAsiento.
    """
    def setUp(self):
        self.periodo = PeriodoFiscal.objects.create(
            nombre="2023",
            fecha_inicio=date(2023, 1, 1),
            fecha_fin=date(2023, 12, 31),
            estado='abierto'
        )
        self.asiento = AsientoContable.objects.create(
            numero="001",
            fecha=date(2023, 10, 26),
            periodo_fiscal=self.periodo,
            concepto="Asiento de prueba"
        )
        self.cuenta = CuentaContable.objects.create(codigo="101", nombre="Caja", tipo="activo")

    def test_linea_asiento_creacion(self):
        """
        Verifica la creación de una línea de asiento.
        """
        linea = LineaAsiento.objects.create(
            asiento=self.asiento,
            cuenta=self.cuenta,
            descripcion="Registro de ingreso",
            debe=500.00
        )
        self.assertEqual(linea.asiento, self.asiento)
        self.assertEqual(linea.cuenta, self.cuenta)
        self.assertEqual(linea.descripcion, "Registro de ingreso")
        self.assertEqual(float(linea.debe), 500.00)
        self.assertEqual(float(linea.haber), 0.00)
        self.assertTrue(isinstance(linea, LineaAsiento))

    def test_linea_asiento_str(self):
        """
        Verifica el método __str__ de LineaAsiento.
        """
        linea_debe = LineaAsiento.objects.create(
            asiento=self.asiento,
            cuenta=self.cuenta,
            debe=500.00
        )
        self.assertEqual(str(linea_debe), f"{self.cuenta} - 500.00")

        linea_haber = LineaAsiento.objects.create(
            asiento=self.asiento,
            cuenta=self.cuenta,
            haber=300.00
        )
        self.assertEqual(str(linea_haber), f"{self.cuenta} - 300.00")

    def test_linea_asiento_validacion_clean(self):
        """
        Verifica la validación del método clean para debe/haber.
        """
        linea_ambos = LineaAsiento(
            asiento=self.asiento,
            cuenta=self.cuenta,
            debe=100.00,
            haber=50.00
        )
        with self.assertRaises(ValidationError):
            linea_ambos.clean()

        linea_ninguno = LineaAsiento(
            asiento=self.asiento,
            cuenta=self.cuenta,
            debe=0.00,
            haber=0.00
        )
        with self.assertRaises(ValidationError):
            linea_ninguno.clean()

        linea_debe_ok = LineaAsiento(
            asiento=self.asiento,
            cuenta=self.cuenta,
            debe=100.00,
            haber=0.00
        )
        linea_debe_ok.clean()

        linea_haber_ok = LineaAsiento(
            asiento=self.asiento,
            cuenta=self.cuenta,
            debe=0.00,
            haber=100.00
        )
        linea_haber_ok.clean()

    def test_linea_asiento_valores_negativos(self):
        """
        Verifica que no se permitan valores negativos en debe o haber.
        """
        linea_debe_negativo = LineaAsiento(
            asiento=self.asiento,
            cuenta=self.cuenta,
            debe=-100.00,
            haber=0.00
        )
        with self.assertRaises(ValidationError):
            linea_debe_negativo.full_clean()

        linea_haber_negativo = LineaAsiento(
            asiento=self.asiento,
            cuenta=self.cuenta,
            debe=0.00,
            haber=-100.00
        )
        with self.assertRaises(ValidationError):
            linea_haber_negativo.full_clean()


class ComprobanteModelTest(TestCase):
    """
    Pruebas para el modelo Comprobante.
    """
    def setUp(self):
        self.proveedor = Proveedor.objects.create(
            nombre="Proveedor Test",
            ruc="1234567890001"
        )
        self.periodo = PeriodoFiscal.objects.create(
            nombre="2023",
            fecha_inicio=date(2023, 1, 1),
            fecha_fin=date(2023, 12, 31),
            estado='abierto'
        )
        self.asiento = AsientoContable.objects.create(
            numero="AST001",
            fecha=date(2023, 11, 1),
            periodo_fiscal=self.periodo,
            concepto="Asiento de comprobante"
        )

    def test_comprobante_creacion(self):
        """
        Verifica la creación de un comprobante.
        """
        comprobante = Comprobante.objects.create(
            numero="FAC001",
            tipo='factura',
            fecha_emision=date(2023, 10, 26),
            proveedor=self.proveedor,
            subtotal=100.00,
            impuestos=12.00,
            total=112.00,
            estado='emitido'
        )
        self.assertEqual(comprobante.numero, "FAC001")
        self.assertEqual(comprobante.tipo, 'factura')
        self.assertEqual(comprobante.fecha_emision, date(2023, 10, 26))
        self.assertEqual(comprobante.proveedor, self.proveedor)
        self.assertEqual(float(comprobante.subtotal), 100.00)
        self.assertEqual(float(comprobante.impuestos), 12.00)
        self.assertEqual(float(comprobante.total), 112.00)
        self.assertEqual(comprobante.estado, 'emitido')
        self.assertIsNone(comprobante.comprobante_relacionado)
        self.assertIsNone(comprobante.asiento_contable)
        self.assertTrue(isinstance(comprobante, Comprobante))

    def test_comprobante_str(self):
        """
        Verifica el método __str__ de Comprobante.
        """
        comprobante = Comprobante.objects.create(
            numero="FAC001",
            tipo='factura',
            fecha_emision=date(2023, 10, 26),
            proveedor=self.proveedor,
            total=112.00,
            estado='emitido'
        )
        self.assertEqual(str(comprobante), f"Factura FAC001 - {self.proveedor}")

    def test_comprobante_numero_unico(self):
        """
        Verifica que el campo numero sea único.
        """
        Comprobante.objects.create(
            numero="FAC001",
            tipo='factura',
            fecha_emision=date(2023, 10, 26),
            proveedor=self.proveedor,
            total=100.00,
            estado='emitido'
        )
        with self.assertRaises(IntegrityError):
            Comprobante.objects.create(
                numero="FAC001",
                tipo='nota_credito',
                fecha_emision=date(2023, 10, 27),
                proveedor=self.proveedor,
                total=50.00,
                estado='emitido'
            )

    def test_comprobante_documentos_relacionados(self):
        """
        Verifica los campos de documentos relacionados y asiento contable.
        """
        comprobante1 = Comprobante.objects.create(
            numero="FAC001",
            tipo='factura',
            fecha_emision=date(2023, 10, 26),
            proveedor=self.proveedor,
            total=100.00,
            estado='emitido'
        )
        comprobante2 = Comprobante.objects.create(
            numero="NC001",
            tipo='nota_credito',
            fecha_emision=date(2023, 10, 27),
            proveedor=self.proveedor,
            total=50.00,
            estado='emitido',
            comprobante_relacionado=comprobante1,
            asiento_contable=self.asiento
        )
        self.assertEqual(comprobante2.comprobante_relacionado, comprobante1)
        self.assertEqual(comprobante2.asiento_contable, self.asiento)
        self.assertIn(comprobante2, comprobante1.comprobantes_relacionados.all())
        self.assertIn(comprobante2, self.asiento.comprobantes.all())

    def test_comprobante_valores_negativos(self):
        """
        Verifica que no se permitan valores negativos en subtotal, impuestos o total.
        """
        with self.assertRaises(ValidationError):
            comprobante = Comprobante(
                numero="FAC002",
                tipo='factura',
                fecha_emision=date(2023, 10, 26),
                proveedor=self.proveedor,
                subtotal=-100.00,
                impuestos=0.00,
                total=-100.00,
                estado='emitido'
            )
            comprobante.full_clean()

        with self.assertRaises(ValidationError):
            comprobante = Comprobante(
                numero="FAC003",
                tipo='factura',
                fecha_emision=date(2023, 10, 26),
                proveedor=self.proveedor,
                subtotal=100.00,
                impuestos=-12.00,
                total=88.00,
                estado='emitido'
            )
            comprobante.full_clean()

        with self.assertRaises(ValidationError):
            comprobante = Comprobante(
                numero="FAC004",
                tipo='factura',
                fecha_emision=date(2023, 10, 26),
                proveedor=self.proveedor,
                subtotal=100.00,
                impuestos=12.00,
                total=-112.00,
                estado='emitido'
            )
            comprobante.full_clean()