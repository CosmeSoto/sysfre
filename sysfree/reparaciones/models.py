from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import ModeloBase
from clientes.models import Cliente


class Reparacion(ModeloBase):
    """Modelo para reparaciones."""
    
    ESTADO_CHOICES = (
        ('recibido', _('Recibido')),
        ('diagnostico', _('En diagnóstico')),
        ('espera_repuestos', _('Esperando repuestos')),
        ('en_reparacion', _('En reparación')),
        ('reparado', _('Reparado')),
        ('entregado', _('Entregado')),
        ('no_reparable', _('No reparable')),
        ('cancelado', _('Cancelado')),
    )
    
    numero = models.CharField(_('número'), max_length=20, unique=True)
    fecha_recepcion = models.DateField(_('fecha de recepción'), auto_now_add=True)
    fecha_estimada_entrega = models.DateField(_('fecha estimada de entrega'), null=True, blank=True)
    fecha_entrega = models.DateField(_('fecha de entrega'), null=True, blank=True)
    cliente = models.ForeignKey(
        Cliente,
        verbose_name=_('cliente'),
        on_delete=models.PROTECT,
        related_name='reparaciones'
    )
    tecnico = models.ForeignKey(
        'core.Usuario',
        verbose_name=_('técnico'),
        on_delete=models.PROTECT,
        related_name='reparaciones_asignadas',
        null=True,
        blank=True
    )
    tipo_equipo = models.CharField(_('tipo de equipo'), max_length=100)
    marca = models.CharField(_('marca'), max_length=100)
    modelo = models.CharField(_('modelo'), max_length=100)
    numero_serie = models.CharField(_('número de serie'), max_length=100, blank=True)
    problema = models.TextField(_('problema reportado'))
    diagnostico = models.TextField(_('diagnóstico'), blank=True)
    solucion = models.TextField(_('solución'), blank=True)
    estado = models.CharField(_('estado'), max_length=20, choices=ESTADO_CHOICES, default='recibido')
    costo_estimado = models.DecimalField(_('costo estimado'), max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(_('total'), max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = _('reparación')
        verbose_name_plural = _('reparaciones')
        ordering = ['-fecha_recepcion']
    
    def __str__(self):
        return f"{self.numero} - {self.cliente} - {self.tipo_equipo}"


class SeguimientoReparacion(ModeloBase):
    """Modelo para seguimientos de reparaciones."""
    
    reparacion = models.ForeignKey(
        Reparacion,
        verbose_name=_('reparación'),
        on_delete=models.CASCADE,
        related_name='seguimientos'
    )
    fecha = models.DateTimeField(_('fecha'), auto_now_add=True)
    estado = models.CharField(_('estado'), max_length=20, choices=Reparacion.ESTADO_CHOICES)
    descripcion = models.TextField(_('descripción'))
    usuario = models.ForeignKey(
        'core.Usuario',
        verbose_name=_('usuario'),
        on_delete=models.PROTECT,
        related_name='seguimientos_reparacion'
    )
    
    class Meta:
        verbose_name = _('seguimiento de reparación')
        verbose_name_plural = _('seguimientos de reparación')
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.reparacion.numero} - {self.get_estado_display()}"