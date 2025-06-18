from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError
from core.models import ModeloBase
from clientes.models import Cliente
from core.models import Usuario

class Reparacion(ModeloBase):
    """Modelo para gestionar reparaciones."""
    
    ESTADO_CHOICES = (
        ('recibido', _('Recibido')),
        ('diagnostico', _('En Diagnóstico')),
        ('reparacion', _('En Reparación')),
        ('finalizado', _('Finalizado')),
        ('entregado', _('Entregado')),
        ('cancelado', _('Cancelado')),
    )
    
    PRIORIDAD_CHOICES = (
        ('baja', _('Baja')),
        ('media', _('Media')),
        ('alta', _('Alta')),
    )
    
    numero = models.CharField(_('número'), max_length=20, unique=True)
    cliente = models.ForeignKey(
        Cliente,
        verbose_name=_('cliente'),
        on_delete=models.PROTECT,
        related_name='reparaciones'
    )
    tipo_equipo = models.CharField(_('tipo de equipo'), max_length=50)
    marca = models.CharField(_('marca'), max_length=50)
    modelo = models.CharField(_('modelo'), max_length=50, blank=True)
    problema_reportado = models.TextField(_('problema reportado'))
    estado = models.CharField(_('estado'), max_length=20, choices=ESTADO_CHOICES, default='recibido')
    prioridad = models.CharField(_('prioridad'), max_length=10, choices=PRIORIDAD_CHOICES, default='media')
    tecnico = models.ForeignKey(
        Usuario,
        verbose_name=_('técnico'),
        on_delete=models.SET_NULL,
        related_name='reparaciones_asignadas',
        null=True,
        blank=True
    )
    costo_diagnostico = models.DecimalField(_('costo diagnóstico'), max_digits=10, decimal_places=2, default=0)
    costo_reparacion = models.DecimalField(_('costo reparación'), max_digits=10, decimal_places=2, default=0)
    costo_repuestos = models.DecimalField(_('costo repuestos'), max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(_('total'), max_digits=10, decimal_places=2, default=0)
    facturado = models.BooleanField(_('facturado'), default=False)
    factura = models.ForeignKey(
        'ventas.Venta',
        verbose_name=_('factura'),
        on_delete=models.SET_NULL,
        related_name='reparaciones',
        null=True,
        blank=True
    )
    public_url = models.URLField(_('URL pública'), max_length=200, blank=True, null=True)
    fecha_recepcion = models.DateTimeField(_('fecha recepción'), auto_now_add=True)
    fecha_estimada_entrega = models.DateField(_('fecha estimada entrega'), null=True, blank=True)
    fecha_entrega = models.DateTimeField(_('fecha entrega'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('reparación')
        verbose_name_plural = _('reparaciones')
        ordering = ['-fecha_recepcion']
    
    def __str__(self):
        return f"{self.numero} - {self.cliente} - {self.tipo_equipo} {self.marca}"
    
    def clean(self):
        """Valida los campos de la reparación."""
        super().clean()
        if self.costo_diagnostico < 0:
            raise ValidationError(_('El costo de diagnóstico no puede ser negativo.'))
        if self.costo_reparacion < 0:
            raise ValidationError(_('El costo de reparación no puede ser negativo.'))
        if self.costo_repuestos < 0:
            raise ValidationError(_('El costo de repuestos no puede ser negativo.'))
        if self.fecha_estimada_entrega and self.fecha_recepcion and self.fecha_estimada_entrega < self.fecha_recepcion.date():
            raise ValidationError(_('La fecha estimada de entrega no puede ser anterior a la fecha de recepción.'))
        if self.fecha_entrega and self.fecha_recepcion and self.fecha_entrega < self.fecha_recepcion:
            raise ValidationError(_('La fecha de entrega no puede ser anterior a la fecha de recepción.'))
    
    def save(self, *args, **kwargs):
        """Calcula el total y guarda la instancia."""
        self.total = self.costo_diagnostico + self.costo_reparacion + self.costo_repuestos
        super().save(*args, **kwargs)