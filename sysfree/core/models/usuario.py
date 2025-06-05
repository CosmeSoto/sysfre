from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _


class UsuarioManager(BaseUserManager):
    """Manager personalizado para el modelo Usuario."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Crea y guarda un usuario con el email y contraseña dados."""
        if not email:
            raise ValueError(_('El email es obligatorio'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Crea y guarda un superusuario con el email y contraseña dados."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superusuario debe tener is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superusuario debe tener is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractUser):
    """Modelo de usuario personalizado que utiliza email como identificador único."""
    
    username = None  # Eliminamos el campo username
    email = models.EmailField(_('correo electrónico'), unique=True)
    nombres = models.CharField(_('nombres'), max_length=150, blank=True)
    apellidos = models.CharField(_('apellidos'), max_length=150, blank=True)
    telefono = models.CharField(_('teléfono'), max_length=15, blank=True)
    foto = models.ImageField(_('foto de perfil'), upload_to='usuarios/fotos/', null=True, blank=True)
    fecha_nacimiento = models.DateField(_('fecha de nacimiento'), null=True, blank=True)
    
    # Campos para auditoría
    fecha_creacion = models.DateTimeField(_('fecha de creación'), auto_now_add=True)
    fecha_modificacion = models.DateTimeField(_('fecha de modificación'), auto_now=True)
    ultimo_login = models.DateTimeField(_('último acceso'), null=True, blank=True)
    
    # Campos para control de acceso
    is_active = models.BooleanField(_('activo'), default=True)
    is_staff = models.BooleanField(_('staff'), default=False)
    
    # Configuración
    objects = UsuarioManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = _('usuario')
        verbose_name_plural = _('usuarios')
        ordering = ['email']
    
    def get_full_name(self):
        """Retorna el nombre completo del usuario."""
        full_name = f"{self.nombres} {self.apellidos}"
        return full_name.strip()
    
    def get_short_name(self):
        """Retorna el nombre corto del usuario."""
        return self.nombres
    
    def __str__(self):
        return self.email