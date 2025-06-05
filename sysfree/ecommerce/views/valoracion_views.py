from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from ..models import Valoracion, ValoracionServicio
from inventario.models import Producto
from reparaciones.models import ServicioReparacion, Reparacion


@login_required
@require_POST
def agregar_valoracion_producto(request, producto_id):
    """Vista para agregar una valoración a un producto."""
    producto = get_object_or_404(Producto, id=producto_id)
    
    # Verificar si el cliente ya ha valorado este producto
    if Valoracion.objects.filter(producto=producto, cliente=request.user.cliente).exists():
        messages.error(request, _("Ya has valorado este producto anteriormente."))
        return redirect('ecommerce:producto_detail', slug=producto.ecommerce.slug)
    
    try:
        puntuacion = int(request.POST.get('puntuacion', 0))
        if puntuacion < 1 or puntuacion > 5:
            raise ValueError(_("La puntuación debe estar entre 1 y 5."))
            
        titulo = request.POST.get('titulo', '').strip()
        comentario = request.POST.get('comentario', '').strip()
        
        if not titulo or not comentario:
            raise ValueError(_("El título y el comentario son obligatorios."))
        
        # Crear la valoración
        valoracion = Valoracion.objects.create(
            producto=producto,
            cliente=request.user.cliente,
            puntuacion=puntuacion,
            titulo=titulo,
            comentario=comentario,
            aprobado=False  # Requiere aprobación del administrador
        )
        
        messages.success(request, _("Tu valoración ha sido enviada y está pendiente de aprobación."))
        
    except ValueError as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, _("Ha ocurrido un error al enviar tu valoración."))
    
    return redirect('ecommerce:producto_detail', slug=producto.ecommerce.slug)


@login_required
@require_POST
def agregar_valoracion_servicio(request, servicio_id, reparacion_id=None):
    """Vista para agregar una valoración a un servicio."""
    servicio = get_object_or_404(ServicioReparacion, id=servicio_id)
    reparacion = None
    
    if reparacion_id:
        reparacion = get_object_or_404(Reparacion, id=reparacion_id, cliente=request.user.cliente)
    
    # Verificar si el cliente ya ha valorado este servicio para esta reparación
    if ValoracionServicio.objects.filter(
        servicio=servicio, 
        cliente=request.user.cliente,
        reparacion=reparacion
    ).exists():
        messages.error(request, _("Ya has valorado este servicio anteriormente."))
        if reparacion:
            return redirect('ecommerce:cuenta_reparacion_detail', numero=reparacion.numero)
        return redirect('ecommerce:servicio_detalle', slug=servicio.ecommerce.slug)
    
    try:
        puntuacion = int(request.POST.get('puntuacion', 0))
        if puntuacion < 1 or puntuacion > 5:
            raise ValueError(_("La puntuación debe estar entre 1 y 5."))
            
        titulo = request.POST.get('titulo', '').strip()
        comentario = request.POST.get('comentario', '').strip()
        
        if not titulo or not comentario:
            raise ValueError(_("El título y el comentario son obligatorios."))
        
        # Crear la valoración
        valoracion = ValoracionServicio.objects.create(
            servicio=servicio,
            cliente=request.user.cliente,
            reparacion=reparacion,
            puntuacion=puntuacion,
            titulo=titulo,
            comentario=comentario,
            aprobado=False  # Requiere aprobación del administrador
        )
        
        messages.success(request, _("Tu valoración ha sido enviada y está pendiente de aprobación."))
        
    except ValueError as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, _("Ha ocurrido un error al enviar tu valoración."))
    
    if reparacion:
        return redirect('ecommerce:cuenta_reparacion_detail', numero=reparacion.numero)
    return redirect('ecommerce:servicio_detalle', slug=servicio.ecommerce.slug)


def obtener_valoraciones_producto(request, producto_id):
    """API para obtener las valoraciones de un producto."""
    producto = get_object_or_404(Producto, id=producto_id)
    valoraciones = Valoracion.objects.filter(producto=producto, aprobado=True)
    
    data = []
    for val in valoraciones:
        data.append({
            'id': val.id,
            'cliente': val.cliente.nombre,
            'puntuacion': val.puntuacion,
            'titulo': val.titulo,
            'comentario': val.comentario,
            'fecha': val.fecha.strftime('%d/%m/%Y')
        })
    
    return JsonResponse({'valoraciones': data})