from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import ModeloBase
from .cliente import Cliente


class ContactoCliente(ModeloBase):
    """Modelo para contactos adicionales de clientes empresariales."""
    
    cliente = models.ForeignKey(
        Cliente,
        verbose_name=_('cliente'),
        on_delete=models.CASCADE,
        related_name='contactos'
    )
    nombres = models.CharField(_('nombres'), max_length=100)
    apellidos = models.CharField(_('apellidos'), max_length=100)
    cargo = models.CharField(_('cargo'), max_length=100, blank=True)
    email = models.EmailField(_('correo electrónico'), blank=True)
    telefono = models.CharField(_('teléfono'), max_length=15, blank=True)
    celular = models.CharField(_('celular'), max_length=15, blank=True)
    es_principal = models.BooleanField(_('es contacto principal'), default=False)
    notas = models.TextField(_('notas'), blank=True)
    
    class Meta:
        verbose_name = _('contacto de cliente')
        verbose_name_plural = _('contactos de clientes')
        ordering = ['cliente', 'nombres', 'apellidos']
    
    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.cliente})"
    
    def save(self, *args, **kwargs):
        """Sobrescribe el método save para asegurar que solo haya un contacto principal por cliente."""
        if self.es_principal:
            # Desmarcar otros contactos principales del mismo cliente
            ContactoCliente.objects.filter(
                cliente=self.cliente, 
                es_principal=True
            ).exclude(pk=self.pk).update(es_principal=False)
        super().save(*args, **kwargs)