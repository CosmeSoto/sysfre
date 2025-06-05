from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from ..models import Pedido, PagoOnline
from ..services.payment_service import PaymentService
import logging

logger = logging.getLogger('sysfree')


@login_required
def paypal_proceso(request):
    """Vista para procesar el pago con PayPal."""
    # Obtener el último pedido pendiente del cliente
    pedido = Pedido.objects.filter(
        cliente=request.user.cliente,
        estado='pendiente'
    ).order_by('-fecha').first()
    
    if not pedido:
        messages.error(request, _("No se encontró un pedido pendiente de pago."))
        return redirect('ecommerce:cuenta_pedidos')
    
    # URL de retorno para PayPal
    return_url = request.build_absolute_uri(reverse('ecommerce:paypal_completado'))
    cancel_url = request.build_absolute_uri(reverse('ecommerce:paypal_cancelado'))
    
    # Crear pago en PayPal
    success, result = PaymentService.crear_pago_paypal(pedido, return_url, cancel_url)
    
    if success:
        # Redireccionar a PayPal
        return redirect(result)
    else:
        # Mostrar error
        messages.error(request, _("Error al procesar el pago: ") + result)
        return redirect('ecommerce:checkout_pago')


@login_required
@csrf_exempt
def paypal_completado(request):
    """Vista para manejar el retorno exitoso de PayPal."""
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')
    
    if not payment_id or not payer_id:
        messages.error(request, _("Información de pago incompleta."))
        return redirect('ecommerce:cuenta_pedidos')
    
    # Ejecutar el pago
    success, message = PaymentService.ejecutar_pago_paypal(payment_id, payer_id)
    
    if success:
        # Obtener el pedido
        try:
            pago = PagoOnline.objects.get(referencia=payment_id)
            pedido = pago.pedido
            
            messages.success(request, _("¡Pago completado con éxito! Tu pedido está siendo procesado."))
            return redirect('ecommerce:checkout_completado', numero_pedido=pedido.numero)
            
        except PagoOnline.DoesNotExist:
            messages.error(request, _("No se encontró el registro de pago."))
            return redirect('ecommerce:cuenta_pedidos')
    else:
        messages.error(request, _("Error al procesar el pago: ") + message)
        return redirect('ecommerce:cuenta_pedidos')


@login_required
def paypal_cancelado(request):
    """Vista para manejar la cancelación del pago en PayPal."""
    payment_id = request.GET.get('paymentId')
    
    if payment_id:
        try:
            pago = PagoOnline.objects.get(referencia=payment_id)
            pago.estado = 'cancelado'
            pago.save()
            
        except PagoOnline.DoesNotExist:
            pass
    
    messages.warning(request, _("Has cancelado el proceso de pago. Tu pedido sigue pendiente."))
    return redirect('ecommerce:cuenta_pedidos')


@login_required
def tarjeta_proceso(request):
    """Vista para procesar el pago con tarjeta de crédito/débito."""
    # Obtener el último pedido pendiente del cliente
    pedido = Pedido.objects.filter(
        cliente=request.user.cliente,
        estado='pendiente'
    ).order_by('-fecha').first()
    
    if not pedido:
        messages.error(request, _("No se encontró un pedido pendiente de pago."))
        return redirect('ecommerce:cuenta_pedidos')
    
    if request.method == 'POST':
        # Obtener el token de Stripe
        token = request.POST.get('stripeToken')
        
        if not token:
            messages.error(request, _("No se recibió información de la tarjeta."))
            return render(request, 'ecommerce/pago/tarjeta_proceso.html', {'pedido': pedido})
        
        # Procesar el pago
        success, result = PaymentService.crear_pago_stripe(pedido, token)
        
        if success:
            messages.success(request, _("¡Pago con tarjeta completado con éxito! Tu pedido está siendo procesado."))
            return redirect('ecommerce:checkout_completado', numero_pedido=pedido.numero)
        else:
            messages.error(request, _("Error al procesar el pago: ") + result)
    
    return render(request, 'ecommerce/pago/tarjeta_proceso.html', {
        'pedido': pedido,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    })


@login_required
def transferencia_instrucciones(request):
    """Vista para mostrar instrucciones de transferencia bancaria."""
    # Obtener el último pedido pendiente del cliente
    pedido = Pedido.objects.filter(
        cliente=request.user.cliente,
        estado='pendiente'
    ).order_by('-fecha').first()
    
    if not pedido:
        messages.error(request, _("No se encontró un pedido pendiente de pago."))
        return redirect('ecommerce:cuenta_pedidos')
    
    # Registrar el pago por transferencia
    success, referencia = PaymentService.registrar_pago_transferencia(pedido)
    
    if not success:
        messages.error(request, _("Error al registrar el pago: ") + referencia)
        return redirect('ecommerce:checkout_pago')
    
    # Datos bancarios (en un entorno real, vendrían de la configuración)
    datos_bancarios = {
        'banco': 'Banco Ejemplo',
        'titular': 'Freecom S.A.',
        'cuenta': '1234-5678-90-1234567890',
        'swift': 'EXAMPLEXXX',
        'referencia': referencia,
    }
    
    return render(request, 'ecommerce/pago/transferencia_instrucciones.html', {
        'pedido': pedido,
        'datos_bancarios': datos_bancarios,
    })


@require_POST
@csrf_exempt
def webhook_stripe(request):
    """Webhook para recibir notificaciones de Stripe."""
    import json
    import stripe
    
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        logger.error(f"Webhook Stripe - Invalid payload: {str(e)}")
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error(f"Webhook Stripe - Invalid signature: {str(e)}")
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    
    # Handle the event
    if event.type == 'charge.succeeded':
        charge = event.data.object
        
        try:
            # Buscar el pago
            pago = PagoOnline.objects.get(referencia=charge.id)
            
            # Actualizar el estado si es necesario
            if pago.estado != 'completado':
                pago.estado = 'completado'
                pago.save()
                
                # Actualizar el pedido
                pedido = pago.pedido
                pedido.estado = 'pagado'
                pedido.save()
                
                logger.info(f"Webhook Stripe - Pago completado: {charge.id} para pedido {pedido.numero}")
                
        except PagoOnline.DoesNotExist:
            logger.error(f"Webhook Stripe - No se encontró el pago: {charge.id}")
    
    return JsonResponse({'status': 'success'})