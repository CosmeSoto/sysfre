from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Reporte, ProgramacionReporte, HistorialReporte


@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'formato', 'es_publico', 'activo')
    list_filter = ('tipo', 'formato', 'es_publico', 'activo')
    search_fields = ('nombre', 'descripcion')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por')
    ordering = ('nombre',)
    
    fieldsets = (
        (None, {'fields': ('nombre', 'descripcion', 'tipo', 'formato')}),
        (_('Configuración'), {'fields': ('consulta_sql', 'parametros', 'plantilla', 'es_publico')}),
        (_('Auditoría'), {'fields': ('activo', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )


@admin.register(ProgramacionReporte)
class ProgramacionReporteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'reporte', 'frecuencia', 'hora', 'ultima_ejecucion', 'proxima_ejecucion', 'activo')
    list_filter = ('frecuencia', 'activo')
    search_fields = ('nombre', 'reporte__nombre', 'destinatarios')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por', 'ultima_ejecucion', 'proxima_ejecucion')
    autocomplete_fields = ['reporte']
    ordering = ('nombre',)
    
    fieldsets = (
        (None, {'fields': ('reporte', 'nombre')}),
        (_('Programación'), {'fields': ('frecuencia', 'hora', 'dia_semana', 'dia_mes', 'mes')}),
        (_('Parámetros'), {'fields': ('parametros',)}),
        (_('Notificación'), {'fields': ('destinatarios', 'asunto', 'mensaje')}),
        (_('Estado'), {'fields': ('ultima_ejecucion', 'proxima_ejecucion')}),
        (_('Auditoría'), {'fields': ('activo', 'creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )


@admin.register(HistorialReporte)
class HistorialReporteAdmin(admin.ModelAdmin):
    list_display = ('reporte', 'programacion', 'fecha_ejecucion', 'duracion', 'estado')
    list_filter = ('estado', 'fecha_ejecucion')
    search_fields = ('reporte__nombre', 'mensaje_error')
    readonly_fields = ('fecha_ejecucion', 'fecha_creacion', 'fecha_modificacion', 'creado_por', 'modificado_por')
    autocomplete_fields = ['reporte', 'programacion']
    ordering = ('-fecha_ejecucion',)
    
    fieldsets = (
        (None, {'fields': ('reporte', 'programacion', 'duracion', 'estado')}),
        (_('Detalles'), {'fields': ('mensaje_error', 'parametros', 'archivo')}),
        (_('Auditoría'), {'fields': ('creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion')}),
    )