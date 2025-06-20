"""
Mixins para integrar auditoría en vistas y formularios.
"""

from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from ..services.auditoria_service import AuditoriaService


class AuditoriaMixin:
    """Mixin para añadir funcionalidad de auditoría a las vistas."""
    
    def get_auditoria_context(self):
        """Obtiene el contexto para auditoría."""
        return {
            'usuario': getattr(self.request, 'user', None),
            'ip': self.request.META.get('REMOTE_ADDR'),
            'user_agent': self.request.META.get('HTTP_USER_AGENT', ''),
            'path': self.request.path,
            'method': self.request.method
        }
    
    def registrar_accion(self, accion, descripcion, **kwargs):
        """Registra una acción de auditoría."""
        context = self.get_auditoria_context()
        AuditoriaService.registrar_actividad_personalizada(
            accion=accion,
            descripcion=descripcion,
            **kwargs
        )


# Señales para auditoría de autenticación
@receiver(user_logged_in)
def auditoria_login_exitoso(sender, request, user, **kwargs):
    """Registra login exitoso."""
    AuditoriaService.login_exitoso(user, request.META.get('REMOTE_ADDR'))


@receiver(user_logged_out)
def auditoria_logout(sender, request, user, **kwargs):
    """Registra logout."""
    if user:
        AuditoriaService.logout(user)


@receiver(user_login_failed)
def auditoria_login_fallido(sender, credentials, request, **kwargs):
    """Registra login fallido."""
    email = credentials.get('username', 'Desconocido')
    ip = request.META.get('REMOTE_ADDR') if request else None
    AuditoriaService.login_fallido(email, ip, "Credenciales inválidas")