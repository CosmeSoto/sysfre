from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from .auditoria import ModeloBase

class TipoIVA(ModeloBase):
    """Modelo para definir tasas de IVA."""

    nombre = models.CharField(_('nombre'), max_length=50, unique=True)
    codigo = models.CharField(_('código'), max_length=20, unique=True)
    porcentaje = models.DecimalField(_('porcentaje'), max_digits=5, decimal_places=2)
    descripcion = models.TextField(_('descripción'), blank=True)
    es_default = models.BooleanField(_('es predeterminado'), default=False)

    class Meta:
        verbose_name = _('tipo de IVA')
        verbose_name_plural = _('tipos de IVA')
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.porcentaje:.2f}%)"

    def clean(self):
        """Valida que el porcentaje no sea negativo y que solo haya un IVA predeterminado."""
        if self.porcentaje < 0:
            raise ValidationError(_('El porcentaje no puede ser negativo.'))
        if self.es_default:
            otros_default = TipoIVA.objects.filter(es_default=True).exclude(id=self.id)
            if otros_default.exists():
                raise ValidationError(_('Solo puede haber un tipo de IVA predeterminado.'))
        super().clean()

    def save(self, *args, **kwargs):
        """Asegura que solo un IVA sea predeterminado."""
        if self.es_default:
            TipoIVA.objects.filter(es_default=True).exclude(id=self.id).update(es_default=False)
        super().save(*args, **kwargs)