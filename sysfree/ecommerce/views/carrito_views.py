from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from ..models import ItemCarrito
from ..services.carrito_service import CarritoService


def carrito_detail(request):
    """Vista para mostrar el detalle del carrito."""
    carrito = CarritoService.obtener_o_crear_carrito(request)
    return render(request, 'ecommerce/carrito/detalle.html', {'carrito': carrito})


@require_POST
def carrito_agregar(request):
    """Vista para agregar un item al carrito."""
    carrito = CarritoService.obtener_o_crear_carrito(request)
    
    try:
        # Determinar si es un producto o un servicio
        if 'servicio_id' in request.POST:
            item_id = request.POST.get('servicio_id')
            es_servicio = True
        else:
            item_id = request.POST.get('producto_id')
            es_servicio = False
            
        cantidad = int(request.POST.get('cantidad', 1))
        
        # Agregar al carrito
        item = CarritoService.agregar_item(carrito, item_id, cantidad, es_servicio)
        
        # Mensaje de éxito
        if es_servicio:
            messages.success(request, _("Servicio añadido al carrito correctamente."))
        else:
            messages.success(request, _("Producto añadido al carrito correctamente."))
        
        # Redireccionar
        next_url = request.POST.get('next', 'ecommerce:carrito_detail')
        return redirect(next_url)
        
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('ecommerce:carrito_detail')
    except Exception as e:
        messages.error(request, _("Ha ocurrido un error al agregar al carrito."))
        return redirect('ecommerce:carrito_detail')


@require_POST
def carrito_actualizar(request, item_id):
    """Vista para actualizar la cantidad de un item en el carrito."""
    carrito = CarritoService.obtener_o_crear_carrito(request)
    
    try:
        cantidad = int(request.POST.get('cantidad', 1))
        item = CarritoService.actualizar_item(carrito, item_id, cantidad)
        messages.success(request, _("Carrito actualizado correctamente."))
        
    except ValueError as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, _("Ha ocurrido un error al actualizar el carrito."))
    
    return redirect('ecommerce:carrito_detail')


@require_POST
def carrito_eliminar(request, item_id):
    """Vista para eliminar un item del carrito."""
    carrito = CarritoService.obtener_o_crear_carrito(request)
    
    try:
        CarritoService.eliminar_item(carrito, item_id)
        messages.success(request, _("Item eliminado del carrito."))
        
    except ValueError as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, _("Ha ocurrido un error al eliminar el item."))
    
    return redirect('ecommerce:carrito_detail')


@require_POST
def carrito_vaciar(request):
    """Vista para vaciar el carrito."""
    carrito = CarritoService.obtener_o_crear_carrito(request)
    
    try:
        CarritoService.vaciar_carrito(carrito)
        messages.success(request, _("Carrito vaciado correctamente."))
        
    except Exception as e:
        messages.error(request, _("Ha ocurrido un error al vaciar el carrito."))
    
    return redirect('ecommerce:carrito_detail')


# API para carrito (AJAX)
def api_carrito_items(request):
    """API para obtener los items del carrito."""
    carrito = CarritoService.obtener_o_crear_carrito(request)
    
    items = []
    for item in carrito.items.all():
        items.append({
            'id': item.id,
            'nombre': str(item.producto) if not item.es_servicio else str(item.item),
            'cantidad': item.cantidad,
            'precio': float(item.precio_unitario),
            'subtotal': float(item.subtotal),
            'es_servicio': item.es_servicio
        })
    
    return JsonResponse({
        'items': items,
        'total_items': carrito.total_items,
        'subtotal': float(carrito.subtotal),
        'total': float(carrito.total)
    })


@require_POST
def api_carrito_agregar(request):
    """API para agregar un item al carrito."""
    carrito = CarritoService.obtener_o_crear_carrito(request)
    
    try:
        # Determinar si es un producto o un servicio
        if 'servicio_id' in request.POST:
            item_id = request.POST.get('servicio_id')
            es_servicio = True
        else:
            item_id = request.POST.get('producto_id')
            es_servicio = False
            
        cantidad = int(request.POST.get('cantidad', 1))
        
        # Agregar al carrito
        item = CarritoService.agregar_item(carrito, item_id, cantidad, es_servicio)
        
        return JsonResponse({
            'success': True,
            'message': _("Item añadido al carrito correctamente."),
            'total_items': carrito.total_items,
            'total': float(carrito.total)
        })
        
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': _("Ha ocurrido un error al agregar al carrito.")
        })


@require_POST
def api_carrito_actualizar(request):
    """API para actualizar la cantidad de un item en el carrito."""
    carrito = CarritoService.obtener_o_crear_carrito(request)
    
    try:
        item_id = int(request.POST.get('item_id'))
        cantidad = int(request.POST.get('cantidad', 1))
        
        item = CarritoService.actualizar_item(carrito, item_id, cantidad)
        
        return JsonResponse({
            'success': True,
            'message': _("Carrito actualizado correctamente."),
            'item_id': item_id,
            'cantidad': item.cantidad,
            'subtotal': float(item.subtotal),
            'total_items': carrito.total_items,
            'subtotal_carrito': float(carrito.subtotal),
            'total_carrito': float(carrito.total)
        })
        
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': _("Ha ocurrido un error al actualizar el carrito.")
        })


@require_POST
def api_carrito_eliminar(request):
    """API para eliminar un item del carrito."""
    carrito = CarritoService.obtener_o_crear_carrito(request)
    
    try:
        item_id = int(request.POST.get('item_id'))
        
        CarritoService.eliminar_item(carrito, item_id)
        
        return JsonResponse({
            'success': True,
            'message': _("Item eliminado del carrito."),
            'item_id': item_id,
            'total_items': carrito.total_items,
            'subtotal': float(carrito.subtotal),
            'total': float(carrito.total)
        })
        
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': _("Ha ocurrido un error al eliminar el item.")
        })