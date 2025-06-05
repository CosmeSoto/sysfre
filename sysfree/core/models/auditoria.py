from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class ModeloBase(models.Model):
    """Modelo base con campos de auditoría para ser heredado por otros modelos."""
    
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('creado por'),
        related_name='%(app_label)s_%(class)s_creados',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    modificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('modificado por'),
        related_name='%(app_label)s_%(class)s_modificados',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    fecha_creacion = models.DateTimeField(_('fecha de creación'), auto_now_add=True)
    fecha_modificacion = models.DateTimeField(_('fecha de modificación'), auto_now=True)
    activo = models.BooleanField(_('activo'), default=True)
    
    class Meta:
        abstract = True


class LogActividad(models.Model):
    """Modelo para registrar actividades importantes en el sistema."""
    
    NIVEL_CHOICES = (
        ('info', _('Información')),
        ('warning', _('Advertencia')),
        ('error', _('Error')),
        ('critical', _('Crítico')),
    )
    
    TIPO_CHOICES = (
        ('sistema', _('Sistema')),
        ('usuario', _('Usuario')),
        ('seguridad', _('Seguridad')),
        ('negocio', _('Negocio')),
    )
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('usuario'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    fecha = models.DateTimeField(_('fecha'), auto_now_add=True)
    ip = models.GenericIPAddressField(_('dirección IP'), null=True, blank=True)
    nivel = models.CharField(_('nivel'), max_length=10, choices=NIVEL_CHOICES, default='info')
    tipo = models.CharField(_('tipo'), max_length=10, choices=TIPO_CHOICES, default='sistema')
    accion = models.CharField(_('acción'), max_length=100)
    descripcion = models.TextField(_('descripción'))
    modelo = models.CharField(_('modelo'), max_length=100, blank=True)
    objeto_id = models.CharField(_('ID del objeto'), max_length=50, blank=True)
    datos = models.JSONField(_('datos adicionales'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('log de actividad')
        verbose_name_plural = _('logs de actividad')
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.fecha} - {self.get_nivel_display()}: {self.accion}"