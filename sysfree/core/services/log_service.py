from ..models import LogActividad
from ..middleware import get_usuario_actual


class LogService:
    """Servicio para registrar actividades en el sistema."""
    
    @classmethod
    def registrar_actividad(cls, accion, descripcion, nivel='info', tipo='sistema', 
                           modelo=None, objeto_id=None, datos=None, ip=None, usuario=None,
                           datos_anteriores=None, user_agent=None):
        """
        Registra una actividad en el sistema.
        
        Args:
            accion (str): Acción realizada
            descripcion (str): Descripción detallada de la acción
            nivel (str): Nivel de la actividad (info, warning, error, critical)
            tipo (str): Tipo de actividad (sistema, usuario, seguridad, negocio)
            modelo (str): Nombre del modelo afectado
            objeto_id (str): ID del objeto afectado
            datos (dict): Datos adicionales
            ip (str): Dirección IP del usuario
            usuario (Usuario): Usuario que realizó la acción
            datos_anteriores (dict): Datos del objeto antes de la modificación
            user_agent (str): User agent del cliente
        
        Returns:
            LogActividad: Instancia del log creado
        """
        if usuario is None:
            usuario = get_usuario_actual()
        
        log = LogActividad.objects.create(
            usuario=usuario,
            nivel=nivel,
            tipo=tipo,
            accion=accion,
            descripcion=descripcion,
            modelo=modelo or '',
            objeto_id=str(objeto_id) if objeto_id else '',
            datos=datos,
            ip=ip,
            datos_anteriores=datos_anteriores,
            user_agent=user_agent
        )
        
        return log
    
    @classmethod
    def info(cls, accion, descripcion, **kwargs):
        """Registra una actividad de nivel info."""
        return cls.registrar_actividad(accion, descripcion, nivel='info', **kwargs)
    
    @classmethod
    def warning(cls, accion, descripcion, **kwargs):
        """Registra una actividad de nivel warning."""
        return cls.registrar_actividad(accion, descripcion, nivel='warning', **kwargs)
    
    @classmethod
    def error(cls, accion, descripcion, **kwargs):
        """Registra una actividad de nivel error."""
        return cls.registrar_actividad(accion, descripcion, nivel='error', **kwargs)
    
    @classmethod
    def critical(cls, accion, descripcion, **kwargs):
        """Registra una actividad de nivel critical."""
        return cls.registrar_actividad(accion, descripcion, nivel='critical', **kwargs)
    
    @classmethod
    def seguridad(cls, accion, descripcion, nivel='info', **kwargs):
        """Registra una actividad de tipo seguridad."""
        return cls.registrar_actividad(accion, descripcion, nivel=nivel, tipo='seguridad', **kwargs)
    
    @classmethod
    def usuario(cls, accion, descripcion, nivel='info', **kwargs):
        """Registra una actividad de tipo usuario."""
        return cls.registrar_actividad(accion, descripcion, nivel=nivel, tipo='usuario', **kwargs)
    
    @classmethod
    def negocio(cls, accion, descripcion, nivel='info', **kwargs):
        """Registra una actividad de tipo negocio."""
        return cls.registrar_actividad(accion, descripcion, nivel=nivel, tipo='negocio', **kwargs)