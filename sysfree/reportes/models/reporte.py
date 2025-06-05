from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import ModeloBase


class Reporte(ModeloBase):
    """Modelo para definir reportes personalizados."""
    
    TIPO_CHOICES = (
        ('ventas', _('Ventas')),
        ('inventario', _('Inventario')),
        ('clientes', _('Clientes')),
        ('reparaciones', _('Reparaciones')),
        ('contabilidad', _('Contabilidad')),
        ('personalizado', _('Personalizado')),
    )
    
    FORMATO_CHOICES = (
        ('pdf', _('PDF')),
        ('excel', _('Excel')),
        ('csv', _('CSV')),
        ('html', _('HTML')),
    )
    
    nombre = models.CharField(_('nombre'), max_length=100)
    descripcion = models.TextField(_('descripción'), blank=True)
    tipo = models.CharField(_('tipo'), max_length=15, choices=TIPO_CHOICES)
    formato = models.CharField(_('formato'), max_length=5, choices=FORMATO_CHOICES, default='pdf')
    consulta_sql = models.TextField(_('consulta SQL'), blank=True)
    parametros = models.JSONField(_('parámetros'), default=dict, blank=True)
    plantilla = models.TextField(_('plantilla'), blank=True)
    es_publico = models.BooleanField(_('es público'), default=False)
    
    class Meta:
        verbose_name = _('reporte')
        verbose_name_plural = _('reportes')
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre