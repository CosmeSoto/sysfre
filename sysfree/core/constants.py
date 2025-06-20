"""
Constantes para el sistema de auditoría y logging.
"""

class AccionesAuditoria:
    """Constantes para acciones de auditoría estandarizadas."""
    
    # Acciones de autenticación
    LOGIN_EXITOSO = "LOGIN_EXITOSO"
    LOGIN_FALLIDO = "LOGIN_FALLIDO"
    LOGOUT = "LOGOUT"
    CAMBIO_PASSWORD = "CAMBIO_PASSWORD"
    RESET_PASSWORD = "RESET_PASSWORD"
    
    # Acciones de usuarios
    USUARIO_CREADO = "USUARIO_CREADO"
    USUARIO_ACTUALIZADO = "USUARIO_ACTUALIZADO"
    USUARIO_ELIMINADO = "USUARIO_ELIMINADO"
    USUARIO_ACTIVADO = "USUARIO_ACTIVADO"
    USUARIO_DESACTIVADO = "USUARIO_DESACTIVADO"
    
    # Acciones de productos/inventario
    PRODUCTO_CREADO = "PRODUCTO_CREADO"
    PRODUCTO_ACTUALIZADO = "PRODUCTO_ACTUALIZADO"
    PRODUCTO_ELIMINADO = "PRODUCTO_ELIMINADO"
    STOCK_ACTUALIZADO = "STOCK_ACTUALIZADO"
    
    # Acciones de ventas
    VENTA_CREADA = "VENTA_CREADA"
    VENTA_ANULADA = "VENTA_ANULADA"
    FACTURA_GENERADA = "FACTURA_GENERADA"
    FACTURA_ANULADA = "FACTURA_ANULADA"
    
    # Acciones de clientes
    CLIENTE_CREADO = "CLIENTE_CREADO"
    CLIENTE_ACTUALIZADO = "CLIENTE_ACTUALIZADO"
    CLIENTE_ELIMINADO = "CLIENTE_ELIMINADO"
    
    # Acciones de configuración
    CONFIGURACION_ACTUALIZADA = "CONFIGURACION_ACTUALIZADA"
    TIPO_IVA_CREADO = "TIPO_IVA_CREADO"
    TIPO_IVA_ACTUALIZADO = "TIPO_IVA_ACTUALIZADO"
    TIPO_IVA_ELIMINADO = "TIPO_IVA_ELIMINADO"
    
    # Acciones de sistema
    BACKUP_CREADO = "BACKUP_CREADO"
    BACKUP_RESTAURADO = "BACKUP_RESTAURADO"
    SISTEMA_ACTUALIZADO = "SISTEMA_ACTUALIZADO"
    
    # Acciones de seguridad
    ACCESO_DENEGADO = "ACCESO_DENEGADO"
    INTENTO_ACCESO_NO_AUTORIZADO = "INTENTO_ACCESO_NO_AUTORIZADO"
    SESION_EXPIRADA = "SESION_EXPIRADA"


class NivelesLog:
    """Constantes para niveles de logging."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class TiposActividad:
    """Constantes para tipos de actividad."""
    SISTEMA = "sistema"
    USUARIO = "usuario"
    SEGURIDAD = "seguridad"
    NEGOCIO = "negocio"


class MensajesAuditoria:
    """Plantillas de mensajes para auditoría."""
    
    @staticmethod
    def creacion(modelo, objeto, usuario=None):
        """Mensaje para creación de objetos."""
        user_info = f" por {usuario.email}" if usuario else ""
        return f"Se creó un nuevo {modelo}: {objeto}{user_info}"
    
    @staticmethod
    def actualizacion(modelo, objeto, usuario=None):
        """Mensaje para actualización de objetos."""
        user_info = f" por {usuario.email}" if usuario else ""
        return f"Se actualizó {modelo}: {objeto}{user_info}"
    
    @staticmethod
    def eliminacion(modelo, objeto, usuario=None):
        """Mensaje para eliminación de objetos."""
        user_info = f" por {usuario.email}" if usuario else ""
        return f"Se eliminó {modelo}: {objeto}{user_info}"
    
    @staticmethod
    def login_exitoso(usuario, ip=None):
        """Mensaje para login exitoso."""
        ip_info = f" desde {ip}" if ip else ""
        return f"Usuario {usuario.email} inició sesión exitosamente{ip_info}"
    
    @staticmethod
    def login_fallido(email, ip=None):
        """Mensaje para login fallido."""
        ip_info = f" desde {ip}" if ip else ""
        return f"Intento de login fallido para {email}{ip_info}"