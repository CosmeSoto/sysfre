from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.contenttypes.models import ContentType
from ..models import ListaDeseos, ItemListaDeseos
from inventario.models import Producto
from reparaciones.models import ServicioReparacion


@login_required
def lista_deseos(request):
    """Vista para mostrar la lista de deseos del cliente."""
    # Obtener o crear la lista de deseos del cliente
    lista, created = ListaDeseos.objects.get_or_create(
        cliente=request.user.cliente,
        defaults={'nombre': _('Mi lista de deseos')}
    )
    
    return render(request, 'ecommerce/lista_deseos/lista.html', {
        'lista': lista,
        'items': lista.items.all()
    })


@login_required
@require_POST
def agregar_a_lista_deseos(request):
    """Vista para agregar un item a la lista de deseos."""
    # Obtener o crear la lista de deseos del cliente
    lista, created = ListaDeseos.objects.get_or_create(
        cliente=request.user.cliente,
        defaults={'nombre': _('Mi lista de deseos')}
    )
    
    try:
        # Determinar si es un producto o un servicio
        if 'servicio_id' in request.POST:
            item_id = request.POST.get('servicio_id')
            es_servicio = True
            servicio = get_object_or_404(ServicioReparacion, id=item_id)
            content_type = ContentType.objects.get_for_model(ServicioReparacion)
            object_id = servicio.id
            
            # Verificar si ya existe en la lista
            if ItemListaDeseos.objects.filter(
                lista=lista,
                content_type=content_type,
                object_id=object_id
            ).exists():
                messages.info(request, _("Este servicio ya está en tu lista de deseos."))
                return redirect('ecommerce:servicio_detalle', slug=servicio.ecommerce.slug)
            
            # Agregar a la lista
            item = ItemListaDeseos.objects.create(
                lista=lista,
                content_type=content_type,
                object_id=object_id,
                es_servicio=True
            )
            
            messages.success(request, _("Servicio añadido a tu lista de deseos."))
            return redirect('ecommerce:servicio_detalle', slug=servicio.ecommerce.slug)
            
        else:
            item_id = request.POST.get('producto_id')
            es_servicio = False
            producto = get_object_or_404(Producto, id=item_id)
            content_type = ContentType.objects.get_for_model(Producto)
            object_id = producto.id
            
            # Verificar si ya existe en la lista
            if ItemListaDeseos.objects.filter(
                lista=lista,
                content_type=content_type,
                object_id=object_id
            ).exists():
                messages.info(request, _("Este producto ya está en tu lista de deseos."))
                return redirect('ecommerce:producto_detail', slug=producto.ecommerce.slug)
            
            # Agregar a la lista
            item = ItemListaDeseos.objects.create(
                lista=lista,
                content_type=content_type,
                object_id=object_id,
                producto=producto,
                es_servicio=False
            )
            
            messages.success(request, _("Producto añadido a tu lista de deseos."))
            return redirect('ecommerce:producto_detail', slug=producto.ecommerce.slug)
            
    except Exception as e:
        messages.error(request, _("Ha ocurrido un error al añadir a tu lista de deseos."))
        return redirect('ecommerce:inicio')


@login_required
@require_POST
def eliminar_de_lista_deseos(request, item_id):
    """Vista para eliminar un item de la lista de deseos."""
    item = get_object_or_404(ItemListaDeseos, id=item_id, lista__cliente=request.user.cliente)
    
    try:
        item.delete()
        messages.success(request, _("Item eliminado de tu lista de deseos."))
    except Exception as e:
        messages.error(request, _("Ha ocurrido un error al eliminar el item."))
    
    return redirect('ecommerce:lista_deseos')