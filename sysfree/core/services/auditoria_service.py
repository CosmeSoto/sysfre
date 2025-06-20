"""
Servicio avanzado de auditoría para SysFree.
"""

from ..middleware import get_usuario_actual, get_request_actual
from ..constants import AccionesAuditoria, NivelesLog, TiposActividad, MensajesAuditoria
from .log_service import LogService


class AuditoriaService:
    """Servicio avanzado para auditoría con métodos específicos por tipo de acción."""
    
    @staticmethod
    def _get_context_info():
        """Obtiene información del contexto actual (usuario, IP, user-agent)."""
        usuario = get_usuario_actual()
        request = get_request_actual()
        
        ip = None
        user_agent = None
        if request:
            ip = request.META.get('REMOTE_ADDR')
            user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        return usuario, ip, user_agent
    
    # Métodos de autenticación
    @classmethod
    def login_exitoso(cls, usuario, ip=None):
        """Registra un login exitoso."""
        usuario_ctx, ip_ctx, user_agent = cls._get_context_info()
        ip = ip or ip_ctx
        
        LogService.seguridad(
            accion=AccionesAuditoria.LOGIN_EXITOSO,
            descripcion=MensajesAuditoria.login_exitoso(usuario, ip),
            usuario=usuario,
            ip=ip,
            user_agent=user_agent,
            datos={'email': usuario.email, 'nombre': usuario.get_full_name()}
        )
    
    @classmethod
    def login_fallido(cls, email, ip=None, razon=None):
        """Registra un intento de login fallido."""
        usuario_ctx, ip_ctx, user_agent = cls._get_context_info()
        ip = ip or ip_ctx
        
        descripcion = MensajesAuditoria.login_fallido(email, ip)
        if razon:
            descripcion += f" - Razón: {razon}"
        
        LogService.seguridad(
            accion=AccionesAuditoria.LOGIN_FALLIDO,
            descripcion=descripcion,
            nivel=NivelesLog.WARNING,
            ip=ip,
            user_agent=user_agent,
            datos={'email': email, 'razon': razon}
        )
    
    @classmethod
    def logout(cls, usuario):
        """Registra un logout."""
        usuario_ctx, ip, user_agent = cls._get_context_info()
        
        LogService.seguridad(
            accion=AccionesAuditoria.LOGOUT,
            descripcion=f"Usuario {usuario.email} cerró sesión",
            usuario=usuario,
            ip=ip,
            user_agent=user_agent
        )
    
    @classmethod
    def cambio_password(cls, usuario):
        """Registra un cambio de contraseña."""
        usuario_ctx, ip, user_agent = cls._get_context_info()
        
        LogService.seguridad(
            accion=AccionesAuditoria.CAMBIO_PASSWORD,
            descripcion=f"Usuario {usuario.email} cambió su contraseña",
            usuario=usuario,
            ip=ip,
            user_agent=user_agent
        )
    
    # Métodos de negocio
    @classmethod
    def venta_creada(cls, venta, detalles=None):
        """Registra la creación de una venta."""
        usuario, ip, user_agent = cls._get_context_info()
        
        datos = {
            'total': str(venta.total) if hasattr(venta, 'total') else None,
            'cliente': str(venta.cliente) if hasattr(venta, 'cliente') else None,
            'items': len(detalles) if detalles else None
        }
        
        LogService.negocio(
            accion=AccionesAuditoria.VENTA_CREADA,
            descripcion=f"Se creó una nueva venta #{venta.id} por valor de ${venta.total if hasattr(venta, 'total') else 'N/A'}",
            usuario=usuario,
            modelo='Venta',
            objeto_id=venta.id,
            datos=datos,
            ip=ip,
            user_agent=user_agent
        )
    
    @classmethod
    def venta_anulada(cls, venta, motivo=None):
        """Registra la anulación de una venta."""
        usuario, ip, user_agent = cls._get_context_info()
        
        descripcion = f"Se anuló la venta #{venta.id}"
        if motivo:
            descripcion += f" - Motivo: {motivo}"
        
        LogService.negocio(
            accion=AccionesAuditoria.VENTA_ANULADA,
            descripcion=descripcion,
            usuario=usuario,
            modelo='Venta',
            objeto_id=venta.id,
            datos={'motivo': motivo, 'total_anulado': str(venta.total) if hasattr(venta, 'total') else None},
            ip=ip,
            user_agent=user_agent,
            nivel=NivelesLog.WARNING
        )
    
    @classmethod
    def stock_actualizado(cls, producto, cantidad_anterior, cantidad_nueva, motivo=None):
        """Registra una actualización de stock."""
        usuario, ip, user_agent = cls._get_context_info()
        
        diferencia = cantidad_nueva - cantidad_anterior
        tipo_movimiento = "Incremento" if diferencia > 0 else "Decremento"
        
        descripcion = f"{tipo_movimiento} de stock para {producto}: {cantidad_anterior} → {cantidad_nueva}"
        if motivo:
            descripcion += f" - {motivo}"
        
        LogService.negocio(
            accion=AccionesAuditoria.STOCK_ACTUALIZADO,
            descripcion=descripcion,
            usuario=usuario,
            modelo='Producto',
            objeto_id=producto.id,
            datos={
                'cantidad_anterior': cantidad_anterior,
                'cantidad_nueva': cantidad_nueva,
                'diferencia': diferencia,
                'motivo': motivo
            },
            ip=ip,
            user_agent=user_agent
        )
    
    # Métodos de configuración
    @classmethod
    def configuracion_actualizada(cls, seccion, cambios):
        """Registra cambios en la configuración del sistema."""
        usuario, ip, user_agent = cls._get_context_info()
        
        LogService.registrar_actividad(
            accion=AccionesAuditoria.CONFIGURACION_ACTUALIZADA,
            descripcion=f"Se actualizó la configuración de {seccion}",
            usuario=usuario,
            tipo=TiposActividad.SISTEMA,
            datos={'seccion': seccion, 'cambios': cambios},
            ip=ip,
            user_agent=user_agent
        )
    
    # Métodos de seguridad
    @classmethod
    def acceso_denegado(cls, recurso, motivo=None):
        """Registra un intento de acceso denegado."""
        usuario, ip, user_agent = cls._get_context_info()
        
        descripcion = f"Acceso denegado al recurso: {recurso}"
        if motivo:
            descripcion += f" - {motivo}"
        
        LogService.seguridad(
            accion=AccionesAuditoria.ACCESO_DENEGADO,
            descripcion=descripcion,
            usuario=usuario,
            nivel=NivelesLog.WARNING,
            datos={'recurso': recurso, 'motivo': motivo},
            ip=ip,
            user_agent=user_agent
        )
    
    @classmethod
    def sesion_expirada(cls, usuario):
        """Registra una sesión expirada."""
        usuario_ctx, ip, user_agent = cls._get_context_info()
        
        LogService.seguridad(
            accion=AccionesAuditoria.SESION_EXPIRADA,
            descripcion=f"Sesión expirada para el usuario {usuario.email}",
            usuario=usuario,
            ip=ip,
            user_agent=user_agent
        )
    
    # Método genérico para auditoría personalizada
    @classmethod
    def registrar_actividad_personalizada(cls, accion, descripcion, nivel=NivelesLog.INFO, 
                                        tipo=TiposActividad.NEGOCIO, modelo=None, 
                                        objeto_id=None, datos=None, datos_anteriores=None):
        """Método genérico para registrar actividades personalizadas."""
        usuario, ip, user_agent = cls._get_context_info()
        
        LogService.registrar_actividad(
            accion=accion,
            descripcion=descripcion,
            nivel=nivel,
            tipo=tipo,
            modelo=modelo,
            objeto_id=objeto_id,
            datos=datos,
            datos_anteriores=datos_anteriores,
            usuario=usuario,
            ip=ip,
            user_agent=user_agent
        )