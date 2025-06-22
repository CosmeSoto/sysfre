import os
import time
import tempfile
from datetime import datetime, timedelta
from django.db import connection
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from ..models import Reporte, HistorialReporte
from core.services.auditoria_service import AuditoriaService


class ReporteService:
    """Servicio para gestionar operaciones de reportes."""
    
    @classmethod
    def ejecutar_reporte(cls, reporte, parametros=None, programacion=None, usuario=None):
        """
        Ejecuta un reporte y genera el archivo correspondiente.
        
        Args:
            reporte: Reporte a ejecutar
            parametros: Parámetros para el reporte
            programacion: Programación que ejecuta el reporte (si aplica)
            usuario: Usuario que ejecuta el reporte
            
        Returns:
            HistorialReporte: Historial de la ejecución del reporte
        """
        parametros = parametros or {}
        inicio = time.time()
        historial = HistorialReporte(
            reporte=reporte,
            programacion=programacion,
            parametros=parametros,
            estado='exito'
        )
        
        if usuario:
            historial.creado_por = usuario
            historial.modificado_por = usuario
        
        try:
            # Ejecutar la consulta SQL
            datos = cls._ejecutar_consulta(reporte.consulta_sql, parametros)
            
            # Generar el archivo según el formato
            archivo = cls._generar_archivo(reporte, datos, parametros)
            
            # Guardar el archivo en el historial
            nombre_archivo = f"{reporte.nombre.lower().replace(' ', '_')}_{timezone.now().strftime('%Y%m%d%H%M%S')}"
            historial.archivo.save(f"{nombre_archivo}.{reporte.formato}", ContentFile(archivo))
            
            # Calcular la duración
            historial.duracion = int(time.time() - inicio)
            
        except Exception as e:
            historial.estado = 'error'
            historial.mensaje_error = str(e)
        
        historial.save()
        
        # Registrar auditoría
        AuditoriaService.registrar_actividad_personalizada(
            accion="REPORTE_EJECUTADO",
            descripcion=f"Reporte ejecutado: {reporte.nombre} - Estado: {historial.estado}",
            modelo="HistorialReporte",
            objeto_id=historial.id,
            datos={
                'reporte': reporte.nombre,
                'formato': reporte.formato,
                'estado': historial.estado,
                'duracion': historial.duracion
            }
        )
        
        # Si es una programación, actualizar la última ejecución
        if programacion:
            programacion.ultima_ejecucion = timezone.now()
            programacion.proxima_ejecucion = cls._calcular_proxima_ejecucion(programacion)
            programacion.save(update_fields=['ultima_ejecucion', 'proxima_ejecucion'])
        
        return historial
    
    @classmethod
    def _ejecutar_consulta(cls, consulta_sql, parametros):
        """
        Ejecuta una consulta SQL con parámetros.
        
        Args:
            consulta_sql: Consulta SQL a ejecutar
            parametros: Parámetros para la consulta
            
        Returns:
            list: Lista de diccionarios con los resultados
        """
        # Reemplazar parámetros en la consulta
        for key, value in parametros.items():
            placeholder = f":{key}"
            if isinstance(value, str):
                value = f"'{value}'"
            consulta_sql = consulta_sql.replace(placeholder, str(value))
        
        # Ejecutar la consulta
        with connection.cursor() as cursor:
            cursor.execute(consulta_sql)
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    @classmethod
    def _generar_archivo(cls, reporte, datos, parametros):
        """
        Genera un archivo con los datos del reporte según el formato.
        
        Args:
            reporte: Reporte a generar
            datos: Datos del reporte
            parametros: Parámetros utilizados
            
        Returns:
            bytes: Contenido del archivo generado
        """
        if reporte.formato == 'pdf':
            return cls._generar_pdf(reporte, datos, parametros)
        elif reporte.formato == 'excel':
            return cls._generar_excel(reporte, datos, parametros)
        elif reporte.formato == 'csv':
            return cls._generar_csv(reporte, datos, parametros)
        elif reporte.formato == 'html':
            return cls._generar_html(reporte, datos, parametros)
        else:
            raise ValueError(f"Formato no soportado: {reporte.formato}")
    
    @classmethod
    def _generar_pdf(cls, reporte, datos, parametros):
        """Genera un archivo PDF con los datos del reporte."""
        # Aquí se implementaría la generación del PDF
        # Por ahora, generamos un HTML y lo convertimos a PDF
        html = cls._generar_html(reporte, datos, parametros)
        
        # Convertir HTML a PDF (requiere una biblioteca como WeasyPrint o xhtml2pdf)
        # Por ahora, devolvemos el HTML como PDF
        return html
    
    @classmethod
    def _generar_excel(cls, reporte, datos, parametros):
        """Genera un archivo Excel con los datos del reporte."""
        import xlsxwriter
        from io import BytesIO
        
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()
        
        # Escribir encabezados
        if datos:
            headers = list(datos[0].keys())
            for col, header in enumerate(headers):
                worksheet.write(0, col, header)
            
            # Escribir datos
            for row, data in enumerate(datos, start=1):
                for col, header in enumerate(headers):
                    worksheet.write(row, col, data.get(header, ''))
        
        workbook.close()
        return output.getvalue()
    
    @classmethod
    def _generar_csv(cls, reporte, datos, parametros):
        """Genera un archivo CSV con los datos del reporte."""
        import csv
        from io import StringIO
        
        output = StringIO()
        if datos:
            headers = list(datos[0].keys())
            writer = csv.DictWriter(output, fieldnames=headers)
            writer.writeheader()
            writer.writerows(datos)
        
        return output.getvalue().encode('utf-8')
    
    @classmethod
    def _generar_html(cls, reporte, datos, parametros):
        """Genera un archivo HTML con los datos del reporte."""
        # Si hay una plantilla personalizada, usarla
        if reporte.plantilla:
            template_string = reporte.plantilla
            html = render_to_string(
                template_string,
                {
                    'reporte': reporte,
                    'datos': datos,
                    'parametros': parametros,
                    'fecha_generacion': timezone.now()
                }
            )
        else:
            # Usar una plantilla genérica
            html = render_to_string(
                'reportes/reporte_generico.html',
                {
                    'reporte': reporte,
                    'datos': datos,
                    'parametros': parametros,
                    'fecha_generacion': timezone.now()
                }
            )
        
        return html.encode('utf-8')
    
    @classmethod
    def _calcular_proxima_ejecucion(cls, programacion):
        """
        Calcula la próxima fecha de ejecución de una programación.
        
        Args:
            programacion: Programación a calcular
            
        Returns:
            datetime: Próxima fecha de ejecución
        """
        now = timezone.now()
        hora = programacion.hora
        
        if programacion.frecuencia == 'diaria':
            # Si la hora ya pasó hoy, programar para mañana
            next_date = now.date()
            if now.time() >= hora:
                next_date += timedelta(days=1)
            return datetime.combine(next_date, hora, tzinfo=timezone.get_current_timezone())
        
        elif programacion.frecuencia == 'semanal':
            # Programar para el próximo día de la semana
            dias_hasta = (programacion.dia_semana - now.weekday()) % 7
            if dias_hasta == 0 and now.time() >= hora:
                dias_hasta = 7
            next_date = now.date() + timedelta(days=dias_hasta)
            return datetime.combine(next_date, hora, tzinfo=timezone.get_current_timezone())
        
        elif programacion.frecuencia == 'mensual':
            # Programar para el día del mes
            next_date = now.replace(day=1)
            if now.day > programacion.dia_mes or (now.day == programacion.dia_mes and now.time() >= hora):
                next_date = (next_date + timedelta(days=32)).replace(day=1)
            
            # Ajustar al día correcto del mes
            import calendar
            _, last_day = calendar.monthrange(next_date.year, next_date.month)
            day = min(programacion.dia_mes, last_day)
            next_date = next_date.replace(day=day)
            
            return datetime.combine(next_date, hora, tzinfo=timezone.get_current_timezone())
        
        elif programacion.frecuencia == 'trimestral':
            # Programar para el día del mes cada 3 meses
            next_date = now.replace(day=1)
            month = ((now.month - 1) // 3) * 3 + 1  # Primer mes del trimestre actual
            next_date = next_date.replace(month=month)
            
            if now.month > month or (now.month == month and now.day > programacion.dia_mes) or \
               (now.month == month and now.day == programacion.dia_mes and now.time() >= hora):
                month = (month + 2) % 12 + 1  # Primer mes del siguiente trimestre
                if month == 1:
                    next_date = next_date.replace(year=next_date.year + 1, month=month)
                else:
                    next_date = next_date.replace(month=month)
            
            # Ajustar al día correcto del mes
            import calendar
            _, last_day = calendar.monthrange(next_date.year, next_date.month)
            day = min(programacion.dia_mes, last_day)
            next_date = next_date.replace(day=day)
            
            return datetime.combine(next_date, hora, tzinfo=timezone.get_current_timezone())
        
        elif programacion.frecuencia == 'anual':
            # Programar para el día y mes del año
            next_date = now.replace(month=programacion.mes, day=1)
            
            if now.month > programacion.mes or \
               (now.month == programacion.mes and now.day > programacion.dia_mes) or \
               (now.month == programacion.mes and now.day == programacion.dia_mes and now.time() >= hora):
                next_date = next_date.replace(year=next_date.year + 1)
            
            # Ajustar al día correcto del mes
            import calendar
            _, last_day = calendar.monthrange(next_date.year, next_date.month)
            day = min(programacion.dia_mes, last_day)
            next_date = next_date.replace(day=day)
            
            return datetime.combine(next_date, hora, tzinfo=timezone.get_current_timezone())
        
        return None