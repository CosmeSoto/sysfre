from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from core.models import ModeloBase
from .cliente import Cliente


class DireccionCliente(ModeloBase):
    """Modelo para direcciones adicionales de clientes."""
    
    TIPO_CHOICES = (
        ('facturacion', _('Facturación')),
        ('envio', _('Envío')),
        ('oficina', _('Oficina')),
        ('casa', _('Casa')),
        ('otro', _('Otro')),
    )
    
    cliente = models.ForeignKey(
        Cliente,
        verbose_name=_('cliente'),
        on_delete=models.CASCADE,
        related_name='direcciones'
    )
    tipo = models.CharField(_('tipo'), max_length=15, choices=TIPO_CHOICES)
    nombre = models.CharField(_('nombre'), max_length=100, blank=True)
    direccion = models.TextField(_('dirección'))
    ciudad = models.CharField(_('ciudad'), max_length=100, blank=True)
    provincia = models.CharField(_('provincia'), max_length=100, blank=True)
    codigo_postal = models.CharField(_('código postal'), max_length=10, blank=True)
    es_principal = models.BooleanField(_('es dirección principal'), default=False)
    notas = models.TextField(_('notas'), blank=True)
    
    # Campos para geolocalización
    latitud = models.DecimalField(_('latitud'), max_digits=10, decimal_places=7, null=True, blank=True)
    longitud = models.DecimalField(_('longitud'), max_digits=10, decimal_places=7, null=True, blank=True)
    
    class Meta:
        verbose_name = _('dirección de cliente')
        verbose_name_plural = _('direcciones de clientes')
        ordering = ['cliente', 'tipo', 'nombre']
    
    def __str__(self):
        if self.nombre:
            return f"{self.nombre} ({self.get_tipo_display()}) - {self.cliente}"
        return f"{self.get_tipo_display()} - {self.cliente}"
    
    def clean(self):
        """Validaciones del modelo."""
        super().clean()
        # Validar que no haya más de una dirección principal por tipo
        if self.es_principal:
            existing = DireccionCliente.objects.filter(
                cliente=self.cliente,
                tipo=self.tipo,
                es_principal=True
            ).exclude(pk=self.pk)
            if existing.exists():
                from django.core.exceptions import ValidationError
                raise ValidationError({
                    'es_principal': f'Ya existe una dirección principal de tipo {self.get_tipo_display()} para este cliente.'
                })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        if self.es_principal:
            DireccionCliente.objects.filter(
                cliente=self.cliente, 
                tipo=self.tipo, 
                es_principal=True
            ).exclude(pk=self.pk).update(es_principal=False)
        super().save(*args, **kwargs)
    
    @property
    def direccion_completa(self):
        """Retorna la dirección completa formateada."""
        partes = [self.direccion]
        if self.ciudad:
            partes.append(self.ciudad)
        if self.provincia:
            partes.append(self.provincia)
        if self.codigo_postal:
            partes.append(self.codigo_postal)
        return ', '.join(partes)