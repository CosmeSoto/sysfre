from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import ModeloBase
from .middleware import get_usuario_actual


@receiver(pre_save)
def pre_save_modelo_base(sender, instance, **kwargs):
    """
    Signal para asignar automáticamente el usuario actual a los campos
    creado_por y modificado_por en modelos que heredan de ModeloBase.
    """
    if not issubclass(sender, ModeloBase):
        return
    
    usuario_actual = get_usuario_actual()
    
    # Si es un objeto nuevo (no tiene ID), asignar el usuario actual como creador
    if not instance.pk and usuario_actual and usuario_actual.is_authenticated:
        instance.creado_por = usuario_actual
    
    # Siempre asignar el usuario actual como modificador
    if usuario_actual and usuario_actual.is_authenticated:
        instance.modificado_por = usuario_actual


@receiver(post_save, sender='core.Usuario')
def actualizar_ultimo_login(sender, instance, **kwargs):
    """
    Signal para actualizar el campo ultimo_login cuando el usuario inicia sesión.
    """
    from django.contrib.auth.signals import user_logged_in
    
    @receiver(user_logged_in)
    def set_ultimo_login(sender, user, request, **kwargs):
        user.ultimo_login = timezone.now()
        user.save(update_fields=['ultimo_login'])