import logging
import uuid
from decimal import Decimal
from django.conf import settings
import stripe
import paypalrestsdk
from ..models import PagoOnline, Pedido

logger = logging.getLogger('sysfree')

# Configurar PayPal
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,  # sandbox o live
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

# Configurar Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentService:
    """Servicio para procesar pagos con diferentes pasarelas."""
    
    @staticmethod
    def crear_pago_paypal(pedido, return_url, cancel_url):
        """
        Crea un pago en PayPal.
        
        Args:
            pedido: Objeto Pedido
            return_url: URL de retorno en caso de éxito
            cancel_url: URL de retorno en caso de cancelación
            
        Returns:
            Tuple con (éxito, url_pago o mensaje_error)
        """
        try:
            # Crear el pago en PayPal
            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "redirect_urls": {
                    "return_url": return_url,
                    "cancel_url": cancel_url
                },
                "transactions": [{
                    "amount": {
                        "total": str(pedido.total),
                        "currency": "USD"
                    },
                    "description": f"Pedido #{pedido.numero} en Freecom"
                }]
            })
            
            # Ejecutar la creación del pago
            if payment.create():
                # Obtener la URL de aprobación
                for link in payment.links:
                    if link.rel == "approval_url":
                        # Guardar el ID de pago de PayPal
                        pago = PagoOnline.objects.create(
                            pedido=pedido,
                            metodo='paypal',
                            estado='pendiente',
                            monto=pedido.total,
                            referencia=payment.id
                        )
                        
                        logger.info(f"Pago PayPal creado: {payment.id} para pedido {pedido.numero}")
                        return True, link.href
                
                logger.error(f"No se encontró URL de aprobación para el pago PayPal: {payment.id}")
                return False, "No se encontró URL de aprobación"
            else:
                logger.error(f"Error al crear pago PayPal: {payment.error}")
                return False, payment.error.get('message', 'Error al crear el pago')
                
        except Exception as e:
            logger.error(f"Error en crear_pago_paypal: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def ejecutar_pago_paypal(payment_id, payer_id):
        """
        Ejecuta un pago en PayPal después de la aprobación del usuario.
        
        Args:
            payment_id: ID del pago en PayPal
            payer_id: ID del pagador
            
        Returns:
            Tuple con (éxito, mensaje)
        """
        try:
            # Obtener el pago
            payment = paypalrestsdk.Payment.find(payment_id)
            
            # Ejecutar el pago
            if payment.execute({"payer_id": payer_id}):
                # Actualizar el registro de pago
                try:
                    pago = PagoOnline.objects.get(referencia=payment_id)
                    pago.estado = 'completado'
                    pago.save()
                    
                    # Actualizar el pedido
                    pedido = pago.pedido
                    pedido.estado = 'pagado'
                    pedido.save()
                    
                    logger.info(f"Pago PayPal ejecutado: {payment_id} para pedido {pedido.numero}")
                    return True, "Pago completado con éxito"
                    
                except PagoOnline.DoesNotExist:
                    logger.error(f"No se encontró el registro de pago para PayPal ID: {payment_id}")
                    return False, "No se encontró el registro de pago"
            else:
                logger.error(f"Error al ejecutar pago PayPal: {payment.error}")
                return False, payment.error.get('message', 'Error al ejecutar el pago')
                
        except Exception as e:
            logger.error(f"Error en ejecutar_pago_paypal: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def crear_pago_stripe(pedido, token):
        """
        Crea un pago en Stripe.
        
        Args:
            pedido: Objeto Pedido
            token: Token de la tarjeta
            
        Returns:
            Tuple con (éxito, charge_id o mensaje_error)
        """
        try:
            # Convertir a centavos para Stripe
            amount_cents = int(pedido.total * 100)
            
            # Crear el cargo en Stripe
            charge = stripe.Charge.create(
                amount=amount_cents,
                currency="usd",
                source=token,
                description=f"Pedido #{pedido.numero} en Freecom",
                metadata={"pedido_id": pedido.id}
            )
            
            # Guardar el registro de pago
            pago = PagoOnline.objects.create(
                pedido=pedido,
                metodo='stripe',
                estado='completado',
                monto=pedido.total,
                referencia=charge.id
            )
            
            # Actualizar el pedido
            pedido.estado = 'pagado'
            pedido.save()
            
            logger.info(f"Pago Stripe creado: {charge.id} para pedido {pedido.numero}")
            return True, charge.id
            
        except stripe.error.CardError as e:
            # Error de tarjeta (fondos insuficientes, tarjeta vencida, etc.)
            logger.error(f"Error de tarjeta Stripe: {str(e)}")
            return False, e.user_message
            
        except stripe.error.StripeError as e:
            # Otros errores de Stripe
            logger.error(f"Error de Stripe: {str(e)}")
            return False, "Error al procesar el pago"
            
        except Exception as e:
            logger.error(f"Error en crear_pago_stripe: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def registrar_pago_transferencia(pedido):
        """
        Registra un pago por transferencia bancaria (pendiente de confirmación).
        
        Args:
            pedido: Objeto Pedido
            
        Returns:
            Tuple con (éxito, referencia o mensaje_error)
        """
        try:
            # Generar referencia única
            referencia = f"TR-{uuid.uuid4().hex[:8].upper()}"
            
            # Guardar el registro de pago
            pago = PagoOnline.objects.create(
                pedido=pedido,
                metodo='transferencia',
                estado='pendiente',
                monto=pedido.total,
                referencia=referencia
            )
            
            logger.info(f"Pago por transferencia registrado: {referencia} para pedido {pedido.numero}")
            return True, referencia
            
        except Exception as e:
            logger.error(f"Error en registrar_pago_transferencia: {str(e)}")
            return False, str(e)