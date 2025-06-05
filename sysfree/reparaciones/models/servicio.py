from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import ModeloBase
from inventario.models import Producto


class ServicioReparacion(ModeloBase):
    """Modelo para servicios de reparación que se pueden ofrecer en la tienda."""
    
    TIPO_CHOICES = (
        ('diagnostico', _('Diagnóstico')),
        ('reparacion', _('Reparación')),
        ('mantenimiento', _('Mantenimiento')),
        ('instalacion', _('Instalación')),
        ('configuracion', _('Configuración')),
        ('otro', _('Otro')),
    )
    
    nombre = models.CharField(_('nombre'), max_length=200)
    descripcion = models.TextField(_('descripción'))
    tipo = models.CharField(_('tipo'), max_length=15, choices=TIPO_CHOICES, default='reparacion')
    precio = models.DecimalField(_('precio'), max_digits=10, decimal_places=2)
    tiempo_estimado = models.PositiveIntegerField(_('tiempo estimado (horas)'), default=1)
    producto = models.OneToOneField(
        Producto,
        verbose_name=_('producto asociado'),
        on_delete=models.CASCADE,
        related_name='servicio_reparacion'
    )
    requiere_diagnostico_previo = models.BooleanField(_('requiere diagnóstico previo'), default=False)
    disponible_online = models.BooleanField(_('disponible online'), default=True)
    
    class Meta:
        verbose_name = _('servicio de reparación')
        verbose_name_plural = _('servicios de reparación')
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre