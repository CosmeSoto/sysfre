from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string
from .models import Cliente
from core.models import Usuario


@receiver(post_save, sender=Cliente)
def crear_usuario_cliente(sender, instance, created, **kwargs):
    """
    Crea un usuario para el cliente si no tiene uno y se ha proporcionado un email.
    """
    if created and instance.email and not instance.usuario:
        # Verificar si ya existe un usuario con ese email
        if not Usuario.objects.filter(email=instance.email).exists():
            # Generar una contraseña aleatoria
            password = get_random_string(12)
            
            # Crear el usuario
            usuario = Usuario.objects.create_user(
                email=instance.email,
                password=password,
                nombres=instance.nombres,
                apellidos=instance.apellidos,
                is_active=True
            )
            
            # Asignar el usuario al cliente
            instance.usuario = usuario
            instance.save(update_fields=['usuario'])
            
            # Enviar email con las credenciales (esto debería implementarse en un servicio)
            # send_welcome_email(instance, password)