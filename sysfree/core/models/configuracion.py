from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models.auditoria import ModeloBase
from django.core.exceptions import ValidationError


class ConfiguracionSistema(ModeloBase):
    """Modelo para configuración general del sistema."""
    
    # Configuración de numeración de documentos
    PREFIJO_FACTURA = models.CharField(_('prefijo factura'), max_length=10, default='FAC-')
    PREFIJO_PROFORMA = models.CharField(_('prefijo proforma'), max_length=10, default='PRO-')
    PREFIJO_NOTA_VENTA = models.CharField(_('prefijo nota de venta'), max_length=10, default='NV-')
    PREFIJO_TICKET = models.CharField(_('prefijo ticket'), max_length=10, default='TIK-')
    
    INICIO_FACTURA = models.PositiveIntegerField(_('inicio numeración factura'), default=1)
    INICIO_PROFORMA = models.PositiveIntegerField(_('inicio numeración proforma'), default=1)
    INICIO_NOTA_VENTA = models.PositiveIntegerField(_('inicio numeración nota de venta'), default=1)
    INICIO_TICKET = models.PositiveIntegerField(_('inicio numeración ticket'), default=1)
    
    # Configuración de impuestos
    tipo_iva_default = models.ForeignKey(
        'TipoIVA',
        verbose_name=_('tipo de IVA predeterminado'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='configuraciones'
    )

    
    class Meta:
        verbose_name = _('configuración del sistema')
        verbose_name_plural = _('configuraciones del sistema')
    
    def __str__(self):
        return 'Configuración del Sistema'
        
    def clean(self):
        """Valida que el tipo_iva_default sea válido."""
        if self.tipo_iva_default and self.tipo_iva_default.porcentaje < 0:
            raise ValidationError(_('El porcentaje de IVA no puede ser negativo.'))
        super().clean()
    
    def save(self, *args, **kwargs):
        """Sobrescribe el método save para asegurar que haya un tipo_iva_default."""
        from core.services import IVAService
        
        # Si no tiene tipo_iva_default asignado, usar el predeterminado del sistema
        if not self.tipo_iva_default:
            self.tipo_iva_default = IVAService.get_default()
            
        super().save(*args, **kwargs)