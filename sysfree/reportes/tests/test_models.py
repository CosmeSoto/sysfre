from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.utils import IntegrityError
from datetime import time, datetime
from reportes.models import Reporte, ProgramacionReporte, HistorialReporte
import json

class ReporteModelTest(TestCase):
    """Pruebas para el modelo Reporte."""
    
    def test_reporte_creacion(self):
        """Verifica la creación de un reporte."""
        reporte = Reporte.objects.create(
            nombre="Reporte de Ventas Mensual",
            descripcion="Ventas por mes",
            tipo="ventas",
            formato="pdf",
            consulta_sql="SELECT * FROM ventas_venta WHERE fecha >= %s",
            parametros={"fecha_inicio": "2023-01-01"},
            plantilla="ventas/reporte_ventas.html",
            es_publico=True
        )
        self.assertEqual(reporte.nombre, "Reporte de Ventas Mensual")
        self.assertEqual(reporte.descripcion, "Ventas por mes")
        self.assertEqual(reporte.tipo, "ventas")
        self.assertEqual(reporte.formato, "pdf")
        self.assertEqual(reporte.consulta_sql, "SELECT * FROM ventas_venta WHERE fecha >= %s")
        self.assertEqual(reporte.parametros, {"fecha_inicio": "2023-01-01"})
        self.assertEqual(reporte.plantilla, "ventas/reporte_ventas.html")
        self.assertTrue(reporte.es_publico)
        self.assertTrue(isinstance(reporte, Reporte))

    def test_reporte_str(self):
        """Verifica el método __str__ de Reporte."""
        reporte = Reporte.objects.create(nombre="Reporte de Ventas")
        self.assertEqual(str(reporte), "Reporte de Ventas")

    def test_reporte_campos_requeridos(self):
        """Verifica que los campos requeridos no sean nulos."""
        with self.assertRaises(ValidationError):
            reporte = Reporte(tipo="ventas", formato="pdf")  # Sin nombre
            reporte.full_clean()

    def test_reporte_tipo_valido(self):
        """Verifica que el tipo sea válido según TIPO_CHOICES."""
        with self.assertRaises(ValidationError):
            reporte = Reporte(
                nombre="Reporte Inválido",
                tipo="invalido",
                formato="pdf"
            )
            reporte.full_clean()

    def test_reporte_formato_valido(self):
        """Verifica que el formato sea válido según FORMATO_CHOICES."""
        with self.assertRaises(ValidationError):
            reporte = Reporte(
                nombre="Reporte Inválido",
                tipo="ventas",
                formato="docx"
            )
            reporte.full_clean()

    def test_reporte_parametros_json(self):
        """Verifica que los parámetros sean un diccionario JSON válido."""
        reporte = Reporte.objects.create(
            nombre="Reporte con Parámetros",
            tipo="ventas",
            formato="pdf",
            parametros={"fecha_inicio": "2023-01-01", "fecha_fin": "2023-12-31"}
        )
        self.assertEqual(reporte.parametros["fecha_inicio"], "2023-01-01")
        self.assertEqual(reporte.parametros["fecha_fin"], "2023-12-31")

class ProgramacionReporteModelTest(TestCase):
    """Pruebas para el modelo ProgramacionReporte."""
    
    def setUp(self):
        self.reporte = Reporte.objects.create(
            nombre="Reporte de Ventas",
            tipo="ventas",
            formato="pdf"
        )

    def test_programacion_creacion(self):
        """Verifica la creación de una programación de reporte."""
        programacion = ProgramacionReporte.objects.create(
            reporte=self.reporte,
            nombre="Programación Mensual",
            frecuencia="mensual",
            hora=time(8, 0),
            dia_mes=1,
            destinatarios="juan@example.com,ana@example.com",
            asunto="Reporte Mensual de Ventas",
            mensaje="Adjunto el reporte mensual",
            parametros={"mes": "2023-01"},
            proxima_ejecucion=datetime(2023, 2, 1, 8, 0)
        )
        self.assertEqual(programacion.reporte, self.reporte)
        self.assertEqual(programacion.nombre, "Programación Mensual")
        self.assertEqual(programacion.frecuencia, "mensual")
        self.assertEqual(programacion.hora, time(8, 0))
        self.assertEqual(programacion.dia_mes, 1)
        self.assertEqual(programacion.destinatarios, "juan@example.com,ana@example.com")
        self.assertEqual(programacion.asunto, "Reporte Mensual de Ventas")
        self.assertEqual(programacion.mensaje, "Adjunto el reporte mensual")
        self.assertEqual(programacion.parametros, {"mes": "2023-01"})
        self.assertEqual(programacion.proxima_ejecucion, datetime(2023, 2, 1, 8, 0))
        self.assertIsNone(programacion.ultima_ejecucion)
        self.assertTrue(isinstance(programacion, ProgramacionReporte))

    def test_programacion_str(self):
        """Verifica el método __str__ de ProgramacionReporte."""
        programacion = ProgramacionReporte.objects.create(
            reporte=self.reporte,
            nombre="Programación Mensual",
            frecuencia="mensual",
            hora=time(8, 0),
            dia_mes=1
        )
        self.assertEqual(str(programacion), f"Programación Mensual - {self.reporte}")

    def test_programacion_relacion_reporte(self):
        """Verifica la relación con Reporte."""
        programacion = ProgramacionReporte.objects.create(
            reporte=self.reporte,
            nombre="Programación Mensual",
            frecuencia="mensual",
            hora=time(8, 0),
            dia_mes=1
        )
        self.assertEqual(programacion.reporte, self.reporte)
        self.assertIn(programacion, self.reporte.programaciones.all())

    def test_programacion_frecuencia_valida(self):
        """Verifica que la frecuencia sea válida según FRECUENCIA_CHOICES."""
        with self.assertRaises(ValidationError):
            programacion = ProgramacionReporte(
                reporte=self.reporte,
                nombre="Programación Inválida",
                frecuencia="bimensual",
                hora=time(8, 0)
            )
            programacion.full_clean()

    def test_programacion_dia_semana_requerido_semanal(self):
        """Verifica que dia_semana sea requerido para frecuencia semanal."""
        with self.assertRaises(ValidationError):
            programacion = ProgramacionReporte(
                reporte=self.reporte,
                nombre="Programación Semanal",
                frecuencia="semanal",
                hora=time(8, 0)
            )
            programacion.full_clean()

    def test_programacion_dia_mes_requerido_mensual(self):
        """Verifica que dia_mes sea requerido para frecuencia mensual."""
        with self.assertRaises(ValidationError):
            programacion = ProgramacionReporte(
                reporte=self.reporte,
                nombre="Programación Mensual",
                frecuencia="mensual",
                hora=time(8, 0)
            )
            programacion.full_clean()

    def test_programacion_destinatarios_formato(self):
        """Verifica que los destinatarios sean correos válidos separados por comas."""
        programacion = ProgramacionReporte(
            reporte=self.reporte,
            nombre="Programación Mensual",
            frecuencia="mensual",
            hora=time(8, 0),
            dia_mes=1,
            destinatarios="juan@example.com, ana@example.com, invalid_email"
        )
        with self.assertRaises(ValidationError):
            programacion.full_clean()

    def test_programacion_parametros_json(self):
        """Verifica que los parámetros sean un diccionario JSON válido."""
        programacion = ProgramacionReporte.objects.create(
            reporte=self.reporte,
            nombre="Programación Mensual",
            frecuencia="mensual",
            hora=time(8, 0),
            dia_mes=1,
            destinatarios="juan@example.com",
            asunto="Reporte",
            parametros={"mes": "2023-01"}
        )
        self.assertEqual(programacion.parametros["mes"], "2023-01")

class HistorialReporteModelTest(TestCase):
    """Pruebas para el modelo HistorialReporte."""
    
    def setUp(self):
        self.reporte = Reporte.objects.create(
            nombre="Reporte de Ventas",
            tipo="ventas",
            formato="pdf"
        )
        self.programacion = ProgramacionReporte.objects.create(
            reporte=self.reporte,
            nombre="Programación Mensual",
            frecuencia="mensual",
            hora=time(8, 0),
            dia_mes=1,
            destinatarios="juan@example.com"
        )

    def test_historial_creacion(self):
        """Verifica la creación de un historial de reporte."""
        historial = HistorialReporte.objects.create(
            reporte=self.reporte,
            programacion=self.programacion,
            duracion=30,
            estado="exito",
            mensaje_error="",
            parametros={"fecha_inicio": "2023-01-01"}
        )
        self.assertEqual(historial.reporte, self.reporte)
        self.assertEqual(historial.programacion, self.programacion)
        self.assertEqual(historial.duracion, 30)
        self.assertEqual(historial.estado, "exito")
        self.assertEqual(historial.mensaje_error, "")
        self.assertEqual(historial.parametros, {"fecha_inicio": "2023-01-01"})
        self.assertIsNotNone(historial.fecha_ejecucion)
        self.assertTrue(isinstance(historial, HistorialReporte))

    def test_historial_str(self):
        """Verifica el método __str__ de HistorialReporte."""
        historial = HistorialReporte.objects.create(
            reporte=self.reporte,
            estado="exito"
        )
        self.assertEqual(str(historial), f"{self.reporte} - {historial.fecha_ejecucion}")

    def test_historial_relaciones(self):
        """Verifica las relaciones con Reporte y ProgramacionReporte."""
        historial = HistorialReporte.objects.create(
            reporte=self.reporte,
            programacion=self.programacion,
            estado="exito"
        )
        self.assertEqual(historial.reporte, self.reporte)
        self.assertEqual(historial.programacion, self.programacion)
        self.assertIn(historial, self.reporte.historial.all())
        self.assertIn(historial, self.programacion.historial.all())

    def test_historial_estado_valido(self):
        """Verifica que el estado sea válido según ESTADO_CHOICES."""
        with self.assertRaises(ValidationError):
            historial = HistorialReporte(
                reporte=self.reporte,
                estado="invalido"
            )
            historial.full_clean()

    def test_historial_duracion_no_negativa(self):
        """Verifica que la duración no sea negativa."""
        with self.assertRaises(ValidationError):
            historial = HistorialReporte(
                reporte=self.reporte,
                estado="exito",
                duracion=-30
            )
            historial.full_clean()

    def test_historial_parametros_json(self):
        """Verifica que los parámetros sean un diccionario JSON válido."""
        historial = HistorialReporte.objects.create(
            reporte=self.reporte,
            estado="exito",
            parametros={"fecha_inicio": "2023-01-01"}
        )
        self.assertEqual(historial.parametros["fecha_inicio"], "2023-01-01")