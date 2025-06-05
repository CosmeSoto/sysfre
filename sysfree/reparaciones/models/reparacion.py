from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import ModeloBase
from clientes.models import Cliente


class Reparacion(ModeloBase):
    """Modelo para reparaciones y servicio técnico."""
    
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
    
    PRIORIDAD_CHOICES = (
        ('baja', _('Baja')),
        ('media', _('Media')),
        ('alta', _('Alta')),
        ('urgente', _('Urgente')),
    )
    
    numero = models.CharField(_('número'), max_length=20, unique=True)
    cliente = models.ForeignKey(
        Cliente,
        verbose_name=_('cliente'),
        on_delete=models.PROTECT,
        related_name='reparaciones'
    )
    fecha_recepcion = models.DateTimeField(_('fecha de recepción'), auto_now_add=True)
    fecha_estimada_entrega = models.DateField(_('fecha estimada de entrega'), null=True, blank=True)
    fecha_entrega = models.DateTimeField(_('fecha de entrega'), null=True, blank=True)
    
    # Información del equipo
    tipo_equipo = models.CharField(_('tipo de equipo'), max_length=100)
    marca = models.CharField(_('marca'), max_length=100)
    modelo = models.CharField(_('modelo'), max_length=100)
    numero_serie = models.CharField(_('número de serie'), max_length=100, blank=True)
    accesorios = models.TextField(_('accesorios'), blank=True)
    
    # Detalles de la reparación
    problema_reportado = models.TextField(_('problema reportado'))
    diagnostico = models.TextField(_('diagnóstico'), blank=True)
    solucion = models.TextField(_('solución'), blank=True)
    observaciones = models.TextField(_('observaciones'), blank=True)
    
    # Estado y seguimiento
    estado = models.CharField(_('estado'), max_length=20, choices=ESTADO_CHOICES, default='recibido')
    prioridad = models.CharField(_('prioridad'), max_length=10, choices=PRIORIDAD_CHOICES, default='media')
    tecnico = models.ForeignKey(
        'core.Usuario',
        verbose_name=_('técnico asignado'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reparaciones_asignadas'
    )
    
    # Costos
    costo_diagnostico = models.DecimalField(_('costo de diagnóstico'), max_digits=10, decimal_places=2, default=0)
    costo_reparacion = models.DecimalField(_('costo de reparación'), max_digits=10, decimal_places=2, default=0)
    costo_repuestos = models.DecimalField(_('costo de repuestos'), max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(_('total'), max_digits=10, decimal_places=2, default=0)
    
    # Facturación
    facturado = models.BooleanField(_('facturado'), default=False)
    factura = models.ForeignKey(
        'ventas.Venta',
        verbose_name=_('factura'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reparaciones'
    )
    
    class Meta:
        verbose_name = _('reparación')
        verbose_name_plural = _('reparaciones')
        ordering = ['-fecha_recepcion']
    
    def __str__(self):
        return f"{self.numero} - {self.cliente} - {self.tipo_equipo} {self.marca}"
    
    def save(self, *args, **kwargs):
        """Sobrescribe el método save para calcular el total."""
        self.total = self.costo_diagnostico + self.costo_reparacion + self.costo_repuestos
        super().save(*args, **kwargs)