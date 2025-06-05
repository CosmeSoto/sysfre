from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from ..models import Comparacion
from inventario.models import Producto


def comparacion(request):
    """Vista para mostrar la comparación de productos."""
    # Obtener IDs de productos de la sesión
    producto_ids = request.session.get('comparacion_productos', [])
    
    # Obtener productos
    productos = Producto.objects.filter(id__in=producto_ids, estado='activo', mostrar_en_tienda=True)
    
    return render(request, 'ecommerce/comparacion/comparacion.html', {
        'productos': productos
    })


@require_POST
def agregar_a_comparacion(request):
    """Vista para agregar un producto a la comparación."""
    producto_id = request.POST.get('producto_id')
    
    if not producto_id:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': _("Producto no especificado.")})
        messages.error(request, _("Producto no especificado."))
        return redirect('ecommerce:inicio')
    
    # Verificar que el producto existe
    try:
        producto = Producto.objects.get(id=producto_id, estado='activo', mostrar_en_tienda=True)
    except Producto.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': _("Producto no encontrado.")})
        messages.error(request, _("Producto no encontrado."))
        return redirect('ecommerce:inicio')
    
    # Obtener o inicializar la lista de productos en comparación
    comparacion_productos = request.session.get('comparacion_productos', [])
    
    # Verificar si el producto ya está en la comparación
    if int(producto_id) in comparacion_productos:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': _("Este producto ya está en la comparación.")})
        messages.info(request, _("Este producto ya está en la comparación."))
        return redirect('ecommerce:producto_detail', slug=producto.ecommerce.slug)
    
    # Limitar a 4 productos
    if len(comparacion_productos) >= 4:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': _("No puedes comparar más de 4 productos. Elimina alguno antes de añadir otro.")})
        messages.warning(request, _("No puedes comparar más de 4 productos. Elimina alguno antes de añadir otro."))
        return redirect('ecommerce:comparacion')
    
    # Agregar el producto a la comparación
    comparacion_productos.append(int(producto_id))
    request.session['comparacion_productos'] = comparacion_productos
    
    # Guardar en la base de datos si el usuario está autenticado
    if request.user.is_authenticated:
        comparacion, created = Comparacion.objects.get_or_create(
            cliente=request.user.cliente,
            defaults={'sesion_id': request.session.session_key}
        )
        comparacion.productos.add(producto)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True, 
            'message': _("Producto añadido a la comparación."),
            'count': len(comparacion_productos)
        })
    
    messages.success(request, _("Producto añadido a la comparación."))
    return redirect('ecommerce:producto_detail', slug=producto.ecommerce.slug)


@require_POST
def eliminar_de_comparacion(request, producto_id):
    """Vista para eliminar un producto de la comparación."""
    # Obtener la lista de productos en comparación
    comparacion_productos = request.session.get('comparacion_productos', [])
    
    # Eliminar el producto de la lista
    if int(producto_id) in comparacion_productos:
        comparacion_productos.remove(int(producto_id))
        request.session['comparacion_productos'] = comparacion_productos
        
        # Actualizar en la base de datos si el usuario está autenticado
        if request.user.is_authenticated:
            try:
                comparacion = Comparacion.objects.get(cliente=request.user.cliente)
                producto = Producto.objects.get(id=producto_id)
                comparacion.productos.remove(producto)
            except (Comparacion.DoesNotExist, Producto.DoesNotExist):
                pass
        
        messages.success(request, _("Producto eliminado de la comparación."))
    
    return redirect('ecommerce:comparacion')


@require_POST
def limpiar_comparacion(request):
    """Vista para eliminar todos los productos de la comparación."""
    # Limpiar la lista de productos en comparación
    if 'comparacion_productos' in request.session:
        del request.session['comparacion_productos']
    
    # Limpiar en la base de datos si el usuario está autenticado
    if request.user.is_authenticated:
        try:
            comparacion = Comparacion.objects.get(cliente=request.user.cliente)
            comparacion.productos.clear()
        except Comparacion.DoesNotExist:
            pass
    
    messages.success(request, _("Comparación limpiada."))
    return redirect('ecommerce:inicio')