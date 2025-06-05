from rest_framework import serializers
from reportes.models import Reporte, ProgramacionReporte, HistorialReporte


class ReporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reporte
        fields = [
            'id', 'nombre', 'descripcion', 'tipo', 'formato', 'consulta_sql',
            'parametros', 'plantilla', 'es_publico', 'activo'
        ]


class ProgramacionReporteSerializer(serializers.ModelSerializer):
    reporte_nombre = serializers.ReadOnlyField(source='reporte.nombre')
    
    class Meta:
        model = ProgramacionReporte
        fields = [
            'id', 'reporte', 'reporte_nombre', 'nombre', 'frecuencia', 'hora',
            'dia_semana', 'dia_mes', 'mes', 'parametros', 'destinatarios',
            'asunto', 'mensaje', 'ultima_ejecucion', 'proxima_ejecucion', 'activo'
        ]
        read_only_fields = ['ultima_ejecucion', 'proxima_ejecucion']


class HistorialReporteSerializer(serializers.ModelSerializer):
    reporte_nombre = serializers.ReadOnlyField(source='reporte.nombre')
    programacion_nombre = serializers.ReadOnlyField(source='programacion.nombre')
    
    class Meta:
        model = HistorialReporte
        fields = [
            'id', 'reporte', 'reporte_nombre', 'programacion', 'programacion_nombre',
            'fecha_ejecucion', 'duracion', 'estado', 'mensaje_error', 'parametros',
            'archivo'
        ]
        read_only_fields = ['fecha_ejecucion']