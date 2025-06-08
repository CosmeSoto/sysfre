from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from core.models import ModeloBase
from .asiento_contable import AsientoContable
from .cuenta_contable import CuentaContable


class LineaAsiento(ModeloBase):
    """Modelo para líneas de asientos contables."""
    
    asiento = models.ForeignKey(
        AsientoContable,
        verbose_name=_('asiento'),
        on_delete=models.CASCADE,
        related_name='lineas'
    )
    cuenta = models.ForeignKey(
        CuentaContable,
        verbose_name=_('cuenta'),
        on_delete=models.PROTECT,
        related_name='lineas_asiento'
    )
    descripcion = models.CharField(_('descripción'), max_length=200, blank=True)
    debe = models.DecimalField(_('debe'), max_digits=12, decimal_places=2, default=0)
    haber = models.DecimalField(_('haber'), max_digits=12, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = _('línea de asiento')
        verbose_name_plural = _('líneas de asiento')
        ordering = ['id']
    
    def __str__(self):
        value = self.debe if self.debe > 0 else self.haber
        return f"{self.cuenta} - {value:.2f}"
    
    def clean(self):
        """Valida que una línea tenga valor en debe o en haber, pero no en ambos, y que no sean negativos."""
        if self.debe > 0 and self.haber > 0:
            raise ValidationError(_('Una línea no puede tener valores en debe y haber simultáneamente.'))
        if self.debe == 0 and self.haber == 0:
            raise ValidationError(_('Una línea debe tener un valor en debe o en haber.'))
        if self.debe < 0 or self.haber < 0:
            raise ValidationError(_('Los valores en debe y haber no pueden ser negativos.'))
        super().clean()