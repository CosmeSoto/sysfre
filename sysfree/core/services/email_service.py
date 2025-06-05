from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger('sysfree')

class EmailService:
    """Servicio para enviar correos electrónicos."""
    
    @staticmethod
    def send_email(subject, template_name, context, recipient_list, from_email=None):
        """
        Envía un correo electrónico usando una plantilla HTML.
        
        Args:
            subject: Asunto del correo
            template_name: Nombre de la plantilla HTML (sin extensión)
            context: Diccionario con el contexto para la plantilla
            recipient_list: Lista de destinatarios
            from_email: Correo del remitente (opcional)
            
        Returns:
            True si el correo se envió correctamente, False en caso contrario
        """
        try:
            if not from_email:
                from_email = settings.DEFAULT_FROM_EMAIL
                
            # Renderizar la plantilla HTML
            html_content = render_to_string(f'emails/{template_name}.html', context)
            text_content = strip_tags(html_content)
            
            # Crear el mensaje
            msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
            msg.attach_alternative(html_content, "text/html")
            
            # Enviar el correo
            msg.send()
            
            logger.info(f"Correo enviado a {', '.join(recipient_list)}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Error al enviar correo: {str(e)}")
            return False
    
    @staticmethod
    def send_order_confirmation(pedido):
        """
        Envía un correo de confirmación de pedido.
        
        Args:
            pedido: Objeto Pedido
            
        Returns:
            True si el correo se envió correctamente, False en caso contrario
        """
        subject = f"Confirmación de pedido #{pedido.numero}"
        template_name = "order_confirmation"
        context = {
            'pedido': pedido,
            'cliente': pedido.cliente,
            'detalles': pedido.detalles.all(),
            'site_url': settings.SITE_URL,
        }
        recipient_list = [pedido.cliente.email]
        
        return EmailService.send_email(subject, template_name, context, recipient_list)
    
    @staticmethod
    def send_order_status_update(pedido):
        """
        Envía un correo de actualización de estado de pedido.
        
        Args:
            pedido: Objeto Pedido
            
        Returns:
            True si el correo se envió correctamente, False en caso contrario
        """
        subject = f"Actualización de pedido #{pedido.numero}"
        template_name = "order_status_update"
        context = {
            'pedido': pedido,
            'cliente': pedido.cliente,
            'estado': pedido.get_estado_display(),
            'site_url': settings.SITE_URL,
        }
        recipient_list = [pedido.cliente.email]
        
        return EmailService.send_email(subject, template_name, context, recipient_list)
    
    @staticmethod
    def send_repair_confirmation(reparacion):
        """
        Envía un correo de confirmación de reparación.
        
        Args:
            reparacion: Objeto Reparacion
            
        Returns:
            True si el correo se envió correctamente, False en caso contrario
        """
        subject = f"Confirmación de reparación #{reparacion.numero}"
        template_name = "repair_confirmation"
        context = {
            'reparacion': reparacion,
            'cliente': reparacion.cliente,
            'site_url': settings.SITE_URL,
        }
        recipient_list = [reparacion.cliente.email]
        
        return EmailService.send_email(subject, template_name, context, recipient_list)
    
    @staticmethod
    def send_repair_status_update(reparacion):
        """
        Envía un correo de actualización de estado de reparación.
        
        Args:
            reparacion: Objeto Reparacion
            
        Returns:
            True si el correo se envió correctamente, False en caso contrario
        """
        subject = f"Actualización de reparación #{reparacion.numero}"
        template_name = "repair_status_update"
        context = {
            'reparacion': reparacion,
            'cliente': reparacion.cliente,
            'estado': reparacion.get_estado_display(),
            'site_url': settings.SITE_URL,
        }
        recipient_list = [reparacion.cliente.email]
        
        return EmailService.send_email(subject, template_name, context, recipient_list)