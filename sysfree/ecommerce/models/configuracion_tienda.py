from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import ModeloBase


class ConfiguracionTienda(ModeloBase):
    """Modelo para configuración de la tienda online."""
    
    nombre_tienda = models.CharField(_('nombre de la tienda'), max_length=100)
    logo = models.ImageField(_('logo'), upload_to='ecommerce/config/', blank=True, null=True)
    favicon = models.ImageField(_('favicon'), upload_to='ecommerce/config/', blank=True, null=True)
    email_contacto = models.EmailField(_('email de contacto'))
    telefono_contacto = models.CharField(_('teléfono de contacto'), max_length=20, blank=True)
    direccion = models.TextField(_('dirección'), blank=True)
    
    # SEO
    meta_titulo = models.CharField(_('meta título'), max_length=100, blank=True)
    meta_descripcion = models.TextField(_('meta descripción'), blank=True)
    meta_keywords = models.CharField(_('meta keywords'), max_length=200, blank=True)
    
    # Redes sociales
    facebook = models.URLField(_('Facebook'), blank=True)
    twitter = models.URLField(_('Twitter'), blank=True)
    instagram = models.URLField(_('Instagram'), blank=True)
    youtube = models.URLField(_('YouTube'), blank=True)
    
    # Configuración de envío
    costo_envio_default = models.DecimalField(_('costo de envío por defecto'), max_digits=10, decimal_places=2, default=0)
    envio_gratis_desde = models.DecimalField(_('envío gratis desde'), max_digits=10, decimal_places=2, default=0)
    
    # Configuración de pagos
    paypal_activo = models.BooleanField(_('PayPal activo'), default=False)
    paypal_client_id = models.CharField(_('PayPal Client ID'), max_length=200, blank=True)
    paypal_secret = models.CharField(_('PayPal Secret'), max_length=200, blank=True)
    
    tarjeta_activo = models.BooleanField(_('Pago con tarjeta activo'), default=False)
    tarjeta_api_key = models.CharField(_('API Key para tarjeta'), max_length=200, blank=True)
    
    transferencia_activo = models.BooleanField(_('Transferencia bancaria activa'), default=False)
    transferencia_instrucciones = models.TextField(_('Instrucciones para transferencia'), blank=True)
    
    efectivo_activo = models.BooleanField(_('Pago en efectivo activo'), default=False)
    
    # Configuración de emails
    email_pedido_cliente = models.BooleanField(_('Enviar email de pedido al cliente'), default=True)
    email_pedido_admin = models.BooleanField(_('Enviar email de pedido al administrador'), default=True)
    email_envio = models.BooleanField(_('Enviar email de envío'), default=True)
    
    class Meta:
        verbose_name = _('configuración de tienda')
        verbose_name_plural = _('configuraciones de tienda')
    
    def __str__(self):
        return self.nombre_tienda
    
    def save(self, *args, **kwargs):
        """Sobrescribe el método save para asegurar que solo haya una configuración activa."""
        # Desactivar otras configuraciones
        if self.activo:
            ConfiguracionTienda.objects.exclude(pk=self.pk).update(activo=False)
        super().save(*args, **kwargs)
    
    @classmethod
    def get_config(cls):
        """Retorna la configuración activa de la tienda."""
        try:
            return cls.objects.get(activo=True)
        except cls.DoesNotExist:
            return None