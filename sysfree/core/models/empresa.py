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
        max_length=1,
        choices=(('1', _('Pruebas')), ('2', _('Producción'))),
        default='1'
    )
    ruta_certificado = models.CharField(
        _('ruta del certificado P12'),
        max_length=255,
        blank=True,
        help_text=_("Ruta absoluta al archivo .p12 en el servidor.")
    )
    clave_certificado = models.CharField(_('clave del certificado'), max_length=255, blank=True)
    
    # URLs de los web services del SRI
    url_recepcion_pruebas = models.URLField(_('URL Recepción (Pruebas)'), blank=True, default='https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl')
    url_autorizacion_pruebas = models.URLField(_('URL Autorización (Pruebas)'), blank=True, default='https://celcer.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl')
    url_recepcion_produccion = models.URLField(_('URL Recepción (Producción)'), blank=True, default='https://cel.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl')
    url_autorizacion_produccion = models.URLField(_('URL Autorización (Producción)'), blank=True, default='https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl')
    
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