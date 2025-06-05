from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.conf import settings
from ..models import Pedido
from ..services.carrito_service import CarritoService
from ..services.pedido_service import PedidoService
from clientes.models import DireccionCliente
import logging

logger = logging.getLogger('sysfree')


@login_required
def checkout(request):
    """Vista para iniciar el proceso de checkout."""
    carrito = CarritoService.obtener_o_crear_carrito(request)
    
    # Verificar si el carrito está vacío
    if not carrito.items.exists():
        messages.warning(request, _("Tu carrito está vacío. Agrega productos antes de continuar."))
        return redirect('ecommerce:carrito_detail')
    
    # Guardar el carrito en la sesión para el proceso de checkout
    request.session['checkout_carrito_id'] = carrito.id
    
    # Redireccionar al primer paso: selección de dirección
    return redirect('ecommerce:checkout_direccion')


@login_required
def checkout_direccion(request):
    """Vista para seleccionar o agregar direcciones de envío y facturación."""
    # Verificar que exista un carrito en proceso de checkout
    carrito_id = request.session.get('checkout_carrito_id')
    if not carrito_id:
        return redirect('ecommerce:checkout')
    
    carrito = CarritoService.obtener_o_crear_carrito(request)
    cliente = request.user.cliente
    direcciones = DireccionCliente.objects.filter(cliente=cliente, activo=True)
    
    if request.method == 'POST':
        direccion_facturacion_id = request.POST.get('direccion_facturacion')
        direccion_envio_id = request.POST.get('direccion_envio')
        misma_direccion = request.POST.get('misma_direccion') == 'on'
        
        if misma_direccion:
            direccion_envio_id = direccion_facturacion_id
        
        # Validar que se hayan seleccionado direcciones
        if not direccion_facturacion_id or not direccion_envio_id:
            messages.error(request, _("Debes seleccionar direcciones de facturación y envío."))
            return render(request, 'ecommerce/checkout/direccion.html', {
                'carrito': carrito,
                'direcciones': direcciones
            })
        
        # Guardar las direcciones seleccionadas en la sesión
        request.session['checkout_direccion_facturacion_id'] = direccion_facturacion_id
        request.session['checkout_direccion_envio_id'] = direccion_envio_id
        
        # Continuar al siguiente paso
        return redirect('ecommerce:checkout_envio')
    
    return render(request, 'ecommerce/checkout/direccion.html', {
        'carrito': carrito,
        'direcciones': direcciones
    })


@login_required
def checkout_envio(request):
    """Vista para seleccionar método de envío."""
    # Verificar que existan direcciones seleccionadas
    if not request.session.get('checkout_direccion_facturacion_id') or not request.session.get('checkout_direccion_envio_id'):
        return redirect('ecommerce:checkout_direccion')
    
    carrito = CarritoService.obtener_o_crear_carrito(request)
    
    # Opciones de envío (podrían venir de la base de datos)
    opciones_envio = [
        {'id': 'estandar', 'nombre': _('Envío Estándar'), 'precio': 5.00, 'tiempo': '3-5 días'},
        {'id': 'express', 'nombre': _('Envío Express'), 'precio': 10.00, 'tiempo': '1-2 días'},
        {'id': 'recogida', 'nombre': _('Recogida en tienda'), 'precio': 0.00, 'tiempo': 'Inmediato'},
    ]
    
    if request.method == 'POST':
        metodo_envio = request.POST.get('metodo_envio')
        
        # Validar que se haya seleccionado un método de envío
        if not metodo_envio:
            messages.error(request, _("Debes seleccionar un método de envío."))
            return render(request, 'ecommerce/checkout/envio.html', {
                'carrito': carrito,
                'opciones_envio': opciones_envio
            })
        
        # Encontrar la opción seleccionada
        opcion_seleccionada = next((o for o in opciones_envio if o['id'] == metodo_envio), None)
        if not opcion_seleccionada:
            messages.error(request, _("El método de envío seleccionado no es válido."))
            return render(request, 'ecommerce/checkout/envio.html', {
                'carrito': carrito,
                'opciones_envio': opciones_envio
            })
        
        # Guardar el método de envío en la sesión
        request.session['checkout_metodo_envio'] = metodo_envio
        request.session['checkout_costo_envio'] = opcion_seleccionada['precio']
        
        # Continuar al siguiente paso
        return redirect('ecommerce:checkout_pago')
    
    return render(request, 'ecommerce/checkout/envio.html', {
        'carrito': carrito,
        'opciones_envio': opciones_envio
    })


@login_required
def checkout_pago(request):
    """Vista para seleccionar método de pago."""
    # Verificar que exista un método de envío seleccionado
    if not request.session.get('checkout_metodo_envio'):
        return redirect('ecommerce:checkout_envio')
    
    carrito = CarritoService.obtener_o_crear_carrito(request)
    costo_envio = request.session.get('checkout_costo_envio', 0)
    
    # Calcular el total con envío
    total_con_envio = carrito.total + float(costo_envio)
    
    # Opciones de pago (podrían venir de la base de datos)
    opciones_pago = [
        {'id': 'paypal', 'nombre': _('PayPal'), 'icono': 'fab fa-paypal'},
        {'id': 'tarjeta', 'nombre': _('Tarjeta de Crédito/Débito'), 'icono': 'far fa-credit-card'},
        {'id': 'transferencia', 'nombre': _('Transferencia Bancaria'), 'icono': 'fas fa-university'},
    ]
    
    if request.method == 'POST':
        metodo_pago = request.POST.get('metodo_pago')
        
        # Validar que se haya seleccionado un método de pago
        if not metodo_pago:
            messages.error(request, _("Debes seleccionar un método de pago."))
            return render(request, 'ecommerce/checkout/pago.html', {
                'carrito': carrito,
                'opciones_pago': opciones_pago,
                'costo_envio': costo_envio,
                'total_con_envio': total_con_envio
            })
        
        # Guardar el método de pago en la sesión
        request.session['checkout_metodo_pago'] = metodo_pago
        
        # Continuar al siguiente paso
        return redirect('ecommerce:checkout_confirmar')
    
    return render(request, 'ecommerce/checkout/pago.html', {
        'carrito': carrito,
        'opciones_pago': opciones_pago,
        'costo_envio': costo_envio,
        'total_con_envio': total_con_envio
    })


@login_required
def checkout_confirmar(request):
    """Vista para confirmar el pedido."""
    # Verificar que exista un método de pago seleccionado
    if not request.session.get('checkout_metodo_pago'):
        return redirect('ecommerce:checkout_pago')
    
    carrito = CarritoService.obtener_o_crear_carrito(request)
    
    # Obtener datos del checkout
    direccion_facturacion = get_object_or_404(
        DireccionCliente, 
        id=request.session.get('checkout_direccion_facturacion_id')
    )
    direccion_envio = get_object_or_404(
        DireccionCliente, 
        id=request.session.get('checkout_direccion_envio_id')
    )
    metodo_envio = request.session.get('checkout_metodo_envio')
    costo_envio = float(request.session.get('checkout_costo_envio', 0))
    metodo_pago = request.session.get('checkout_metodo_pago')
    
    # Calcular el total con envío
    total_con_envio = carrito.total + costo_envio
    
    if request.method == 'POST':
        notas = request.POST.get('notas', '')
        
        try:
            # Crear el pedido
            pedido = PedidoService.crear_pedido_desde_carrito(
                carrito=carrito,
                direccion_facturacion=direccion_facturacion,
                direccion_envio=direccion_envio,
                notas=notas
            )
            
            # Actualizar el pedido con los datos de envío
            pedido.envio = costo_envio
            pedido.total += costo_envio
            pedido.save()
            
            # Limpiar datos de checkout de la sesión
            for key in list(request.session.keys()):
                if key.startswith('checkout_'):
                    del request.session[key]
            
            # Redireccionar según el método de pago
            if metodo_pago == 'paypal':
                return redirect('ecommerce:paypal_proceso')
            elif metodo_pago == 'tarjeta':
                return redirect('ecommerce:tarjeta_proceso')
            elif metodo_pago == 'transferencia':
                return redirect('ecommerce:transferencia_instrucciones')
            else:
                # Por defecto, ir a la página de pedido completado
                return redirect('ecommerce:checkout_completado', numero_pedido=pedido.numero)
                
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            logger.error(f"Error al crear pedido: {str(e)}")
            messages.error(request, _("Ha ocurrido un error al procesar tu pedido. Por favor, inténtalo de nuevo."))
    
    return render(request, 'ecommerce/checkout/confirmar.html', {
        'carrito': carrito,
        'direccion_facturacion': direccion_facturacion,
        'direccion_envio': direccion_envio,
        'metodo_envio': metodo_envio,
        'costo_envio': costo_envio,
        'metodo_pago': metodo_pago,
        'total_con_envio': total_con_envio
    })


@login_required
def checkout_completado(request, numero_pedido):
    """Vista para mostrar la confirmación de pedido completado."""
    pedido = get_object_or_404(Pedido, numero=numero_pedido, cliente=request.user.cliente)
    
    return render(request, 'ecommerce/checkout/completado.html', {
        'pedido': pedido
    })