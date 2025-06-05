from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import ModeloBase


class Cliente(ModeloBase):
    """Modelo para clientes."""
    
    TIPO_IDENTIFICACION_CHOICES = (
        ('cedula', _('Cédula')),
        ('ruc', _('RUC')),
        ('pasaporte', _('Pasaporte')),
    )
    
    TIPO_CLIENTE_CHOICES = (
        ('persona', _('Persona Natural')),
        ('empresa', _('Empresa')),
    )
    
    tipo_identificacion = models.CharField(_('tipo de identificación'), max_length=10, choices=TIPO_IDENTIFICACION_CHOICES)
    identificacion = models.CharField(_('identificación'), max_length=20, unique=True)
    nombres = models.CharField(_('nombres'), max_length=100)
    apellidos = models.CharField(_('apellidos'), max_length=100, blank=True)
    nombre_comercial = models.CharField(_('nombre comercial'), max_length=200, blank=True)
    tipo_cliente = models.CharField(_('tipo de cliente'), max_length=10, choices=TIPO_CLIENTE_CHOICES, default='persona')
    email = models.EmailField(_('correo electrónico'), blank=True)
    telefono = models.CharField(_('teléfono'), max_length=15, blank=True)
    celular = models.CharField(_('celular'), max_length=15, blank=True)
    direccion = models.TextField(_('dirección'), blank=True)
    fecha_nacimiento = models.DateField(_('fecha de nacimiento'), null=True, blank=True)
    
    # Campos para crédito
    limite_credito = models.DecimalField(_('límite de crédito'), max_digits=10, decimal_places=2, default=0)
    dias_credito = models.PositiveIntegerField(_('días de crédito'), default=0)
    
    # Campos para marketing
    recibir_promociones = models.BooleanField(_('recibir promociones'), default=True)
    
    # Campos para portal de cliente
    usuario = models.OneToOneField(
        'core.Usuario',
        verbose_name=_('usuario'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cliente'
    )
    
    class Meta:
        verbose_name = _('cliente')
        verbose_name_plural = _('clientes')
        ordering = ['nombres', 'apellidos']
    
    def __str__(self):
        if self.tipo_cliente == 'empresa':
            return self.nombre_comercial or self.nombres
        return f"{self.nombres} {self.apellidos}".strip()
    
    @property
    def nombre_completo(self):
        """Retorna el nombre completo del cliente."""
        if self.tipo_cliente == 'empresa':
            return self.nombre_comercial or self.nombres
        return f"{self.nombres} {self.apellidos}".strip()
    
    @property
    def tiene_acceso_portal(self):
        """Indica si el cliente tiene acceso al portal de clientes."""
        return self.usuario is not None and self.usuario.is_active