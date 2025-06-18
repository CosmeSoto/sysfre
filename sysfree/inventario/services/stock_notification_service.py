"""
Servicio para notificar a los administradores cuando el stock de un producto baja de cierto umbral.
"""
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.utils import timezone
from inventario.models import Producto, AlertaStock

User = get_user_model()

class StockNotificationService:
    """Servicio para notificar a los administradores cuando el stock de un producto baja de cierto umbral."""
    
    @staticmethod
    def notificar_stock_bajo(producto):
        """
        Notifica a los administradores cuando el stock de un producto baja de cierto umbral.
        
        Args:
            producto: Objeto Producto
        """
        if not producto.es_inventariable:
            return
            
        if producto.stock <= producto.stock_minimo:
            # Verificar si ya existe una alerta pendiente para este producto
            alerta_existente = AlertaStock.objects.filter(
                producto=producto,
                estado__in=['pendiente', 'en_proceso']
            ).first()
            
            if not alerta_existente:
                # Crear nueva alerta
                alerta = AlertaStock.objects.create(
                    producto=producto,
                    stock_actual=producto.stock,
                    stock_minimo=producto.stock_minimo,
                    estado='pendiente'
                )
                
                # Obtener administradores
                admins = User.objects.filter(is_staff=True, is_active=True)
                
                # Enviar correo electrónico
                subject = _('Alerta de stock bajo: {}').format(producto.nombre)
                message = _("""
                El stock del producto {nombre} ha bajado del umbral mínimo.
                
                Código: {codigo}
                Stock actual: {stock}
                Stock mínimo: {stock_minimo}
                
                Por favor, reabastezca este producto lo antes posible.
                """).format(
                    nombre=producto.nombre,
                    codigo=producto.codigo,
                    stock=producto.stock,
                    stock_minimo=producto.stock_minimo
                )
                
                from_email = settings.DEFAULT_FROM_EMAIL
                recipient_list = [admin.email for admin in admins]
                
                try:
                    send_mail(subject, message, from_email, recipient_list)
                    alerta.notificado = True
                    alerta.save()
                except Exception as e:
                    import logging
                    logger = logging.getLogger('sysfree')
                    logger.error(f"Error al enviar notificación de stock bajo para {producto.nombre}: {str(e)}")
    
    @staticmethod
    def verificar_productos_stock_bajo():
        """
        Verifica todos los productos y notifica a los administradores si alguno tiene stock bajo.
        """
        productos = Producto.objects.filter(es_inventariable=True, activo=True)
        
        for producto in productos:
            if producto.stock <= producto.stock_minimo:
                StockNotificationService.notificar_stock_bajo(producto)
    
    @staticmethod
    def resolver_alerta(alerta_id, notas=''):
        """
        Marca una alerta como resuelta.
        
        Args:
            alerta_id: ID de la alerta
            notas: Notas adicionales
        """
        try:
            alerta = AlertaStock.objects.get(id=alerta_id)
            alerta.estado = 'resuelta'
            alerta.fecha_resolucion = timezone.now()
            alerta.notas = notas
            alerta.save()
            return True
        except AlertaStock.DoesNotExist:
            return False