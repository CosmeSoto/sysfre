from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import ModeloBase


class CuentaContable(ModeloBase):
    """Modelo para cuentas contables."""
    
    TIPO_CHOICES = (
        ('activo', _('Activo')),
        ('pasivo', _('Pasivo')),
        ('patrimonio', _('Patrimonio')),
        ('ingreso', _('Ingreso')),
        ('gasto', _('Gasto')),
    )
    
    codigo = models.CharField(_('código'), max_length=20, unique=True)
    nombre = models.CharField(_('nombre'), max_length=100)
    tipo = models.CharField(_('tipo'), max_length=10, choices=TIPO_CHOICES)
    cuenta_padre = models.ForeignKey(
        'self',
        verbose_name=_('cuenta padre'),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcuentas'
    )
    descripcion = models.TextField(_('descripción'), blank=True)
    
    class Meta:
        verbose_name = _('cuenta contable')
        verbose_name_plural = _('cuentas contables')
        ordering = ['codigo']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    @property
    def ruta_completa(self):
        """Retorna la ruta completa de la cuenta (incluyendo padres)."""
        if self.cuenta_padre:
            return f"{self.cuenta_padre.ruta_completa} > {self.nombre}"
        return self.nombre