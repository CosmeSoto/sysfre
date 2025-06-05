from django.db import models
from django.utils.translation import gettext_lazy as _
from .auditoria import ModeloBase


class Empresa(ModeloBase):
    """Modelo para almacenar información de la empresa."""
    
    nombre = models.CharField(_('nombre'), max_length=200)
    nombre_comercial = models.CharField(_('nombre comercial'), max_length=200, blank=True)
    ruc = models.CharField(_('RUC'), max_length=13, unique=True)
    direccion = models.TextField(_('dirección'))
    telefono = models.CharField(_('teléfono'), max_length=15, blank=True)
    email = models.EmailField(_('correo electrónico'), blank=True)
    sitio_web = models.URLField(_('sitio web'), blank=True)
    logo = models.ImageField(_('logo'), upload_to='empresa/logos/', null=True, blank=True)
    
    # Información fiscal
    regimen_fiscal = models.CharField(_('régimen fiscal'), max_length=100, blank=True)
    representante_legal = models.CharField(_('representante legal'), max_length=200, blank=True)
    cedula_representante = models.CharField(_('cédula del representante'), max_length=10, blank=True)
    
    # Información adicional
    descripcion = models.TextField(_('descripción'), blank=True)
    horario = models.TextField(_('horario de atención'), blank=True)
    
    # Redes sociales
    facebook = models.URLField(_('Facebook'), blank=True)
    instagram = models.URLField(_('Instagram'), blank=True)
    twitter = models.URLField(_('Twitter'), blank=True)
    
    # Configuración de facturación electrónica
    ambiente_facturacion = models.CharField(
        _('ambiente de facturación'),
        max_length=10,
        choices=(('pruebas', _('Pruebas')), ('produccion', _('Producción'))),
        default='pruebas'
    )
    certificado_digital = models.FileField(
        _('certificado digital'),
        upload_to='empresa/certificados/',
        null=True,
        blank=True
    )
    clave_certificado = models.CharField(_('clave del certificado'), max_length=100, blank=True)
    
    class Meta:
        verbose_name = _('empresa')
        verbose_name_plural = _('empresas')
    
    def __str__(self):
        return self.nombre


class Sucursal(ModeloBase):
    """Modelo para almacenar información de sucursales de la empresa."""
    
    empresa = models.ForeignKey(
        Empresa,
        verbose_name=_('empresa'),
        related_name='sucursales',
        on_delete=models.CASCADE
    )
    nombre = models.CharField(_('nombre'), max_length=200)
    codigo = models.CharField(_('código'), max_length=10)
    direccion = models.TextField(_('dirección'))
    telefono = models.CharField(_('teléfono'), max_length=15, blank=True)
    email = models.EmailField(_('correo electrónico'), blank=True)
    es_matriz = models.BooleanField(_('es matriz'), default=False)
    horario = models.TextField(_('horario de atención'), blank=True)
    
    class Meta:
        verbose_name = _('sucursal')
        verbose_name_plural = _('sucursales')
        unique_together = ('empresa', 'codigo')
    
    def __str__(self):
        return f"{self.nombre} ({self.codigo})"