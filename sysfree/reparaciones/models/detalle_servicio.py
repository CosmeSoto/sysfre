from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from core.models import ModeloBase
from .reparacion import Reparacion
from .servicio import ServicioReparacion


class DetalleServicio(ModeloBase):
    """Modelo para detalles de servicios en una reparación."""
    
    reparacion = models.ForeignKey(
        Reparacion,
        verbose_name=_('reparación'),
        on_delete=models.CASCADE,
        related_name='detalles_servicio'
    )
    servicio = models.ForeignKey(
        ServicioReparacion,
        verbose_name=_('servicio'),
        on_delete=models.PROTECT,
        related_name='detalles'
    )
    precio = models.DecimalField(_('precio'), max_digits=10, decimal_places=2)
    notas = models.TextField(_('notas'), blank=True)
    completado = models.BooleanField(_('completado'), default=False)
    fecha_completado = models.DateTimeField(_('fecha completado'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('detalle de servicio')
        verbose_name_plural = _('detalles de servicio')
        ordering = ['id']
        unique_together = ['reparacion', 'servicio']
    
    def __str__(self):
        return f"{self.servicio} - {self.reparacion}"
    
    def clean(self):
        """Valida que el precio no sea negativo."""
        if self.precio < 0:
            raise ValidationError(_('El precio no puede ser negativo.'))
        super().clean()
    
    def save(self, *args, **kwargs):
        """Actualiza el costo de reparación y el total de la reparación."""
        super().save(*args, **kwargs)
        
        # Actualizar el costo de reparación y el total de la reparación
        reparacion = self.reparacion
        detalles = DetalleServicio.objects.filter(reparacion=reparacion)
        reparacion.costo_reparacion = sum(detalle.precio for detalle in detalles)
        reparacion.save()