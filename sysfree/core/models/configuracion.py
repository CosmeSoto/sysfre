from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models.auditoria import ModeloBase


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
    IVA_PORCENTAJE = models.DecimalField(_('porcentaje IVA'), max_digits=5, decimal_places=2, default=12.00)
    
    # Configuración de empresa
    NOMBRE_EMPRESA = models.CharField(_('nombre de la empresa'), max_length=100, default='Mi Empresa')
    RUC = models.CharField(_('RUC'), max_length=13, blank=True)
    DIRECCION = models.TextField(_('dirección'), blank=True)
    TELEFONO = models.CharField(_('teléfono'), max_length=20, blank=True)
    EMAIL = models.EmailField(_('email'), blank=True)
    SITIO_WEB = models.URLField(_('sitio web'), blank=True)
    
    # Configuración de facturación electrónica
    AMBIENTE_FACTURACION = models.CharField(
        _('ambiente de facturación'),
        max_length=10,
        choices=(('pruebas', _('Pruebas')), ('produccion', _('Producción'))),
        default='pruebas'
    )
    CLAVE_CERTIFICADO = models.CharField(_('clave del certificado'), max_length=100, blank=True)
    RUTA_CERTIFICADO = models.CharField(_('ruta del certificado'), max_length=255, blank=True)
    
    class Meta:
        verbose_name = _('configuración del sistema')
        verbose_name_plural = _('configuraciones del sistema')
    
    def __str__(self):
        return self.NOMBRE_EMPRESA