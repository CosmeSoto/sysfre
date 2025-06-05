from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from ..models import Pedido
from clientes.models import DireccionCliente
from reparaciones.models import Reparacion
import logging

logger = logging.getLogger('sysfree')


@login_required
def cuenta_dashboard(request):
    """Vista para el panel de control del cliente."""
    cliente = request.user.cliente
    
    # Obtener últimos pedidos
    pedidos_recientes = Pedido.objects.filter(cliente=cliente).order_by('-fecha')[:5]
    
    # Obtener últimas reparaciones
    reparaciones_recientes = Reparacion.objects.filter(cliente=cliente).order_by('-fecha_recepcion')[:5]
    
    return render(request, 'ecommerce/cuenta/dashboard.html', {
        'cliente': cliente,
        'pedidos_recientes': pedidos_recientes,
        'reparaciones_recientes': reparaciones_recientes,
    })


@login_required
def cuenta_pedidos(request):
    """Vista para listar los pedidos del cliente."""
    cliente = request.user.cliente
    pedidos_list = Pedido.objects.filter(cliente=cliente).order_by('-fecha')
    
    # Paginación
    paginator = Paginator(pedidos_list, 10)
    page = request.GET.get('page', 1)
    pedidos = paginator.get_page(page)
    
    return render(request, 'ecommerce/cuenta/pedidos.html', {
        'pedidos': pedidos,
    })


@login_required
def cuenta_pedido_detail(request, numero_pedido):
    """Vista para mostrar el detalle de un pedido."""
    pedido = get_object_or_404(Pedido, numero=numero_pedido, cliente=request.user.cliente)
    
    return render(request, 'ecommerce/cuenta/pedido_detalle.html', {
        'pedido': pedido,
    })


@login_required
def cuenta_direcciones(request):
    """Vista para listar las direcciones del cliente."""
    cliente = request.user.cliente
    direcciones = DireccionCliente.objects.filter(cliente=cliente, activo=True)
    
    return render(request, 'ecommerce/cuenta/direcciones.html', {
        'direcciones': direcciones,
    })


@login_required
def cuenta_direccion_agregar(request):
    """Vista para agregar una nueva dirección."""
    from clientes.forms import DireccionClienteForm
    
    if request.method == 'POST':
        form = DireccionClienteForm(request.POST)
        if form.is_valid():
            direccion = form.save(commit=False)
            direccion.cliente = request.user.cliente
            direccion.save()
            messages.success(request, _("Dirección agregada correctamente."))
            return redirect('ecommerce:cuenta_direcciones')
    else:
        form = DireccionClienteForm()
    
    return render(request, 'ecommerce/cuenta/direccion_form.html', {
        'form': form,
        'titulo': _("Agregar dirección"),
    })


@login_required
def cuenta_direccion_editar(request, pk):
    """Vista para editar una dirección existente."""
    from clientes.forms import DireccionClienteForm
    
    direccion = get_object_or_404(DireccionCliente, pk=pk, cliente=request.user.cliente)
    
    if request.method == 'POST':
        form = DireccionClienteForm(request.POST, instance=direccion)
        if form.is_valid():
            form.save()
            messages.success(request, _("Dirección actualizada correctamente."))
            return redirect('ecommerce:cuenta_direcciones')
    else:
        form = DireccionClienteForm(instance=direccion)
    
    return render(request, 'ecommerce/cuenta/direccion_form.html', {
        'form': form,
        'titulo': _("Editar dirección"),
        'direccion': direccion,
    })


@login_required
def cuenta_perfil(request):
    """Vista para editar el perfil del cliente."""
    from clientes.forms import ClienteForm
    
    cliente = request.user.cliente
    
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, _("Perfil actualizado correctamente."))
            return redirect('ecommerce:cuenta_dashboard')
    else:
        form = ClienteForm(instance=cliente)
    
    return render(request, 'ecommerce/cuenta/perfil.html', {
        'form': form,
    })


@login_required
def cuenta_reparaciones(request):
    """Vista para listar las reparaciones del cliente."""
    cliente = request.user.cliente
    reparaciones_list = Reparacion.objects.filter(cliente=cliente).order_by('-fecha_recepcion')
    
    # Paginación
    paginator = Paginator(reparaciones_list, 10)
    page = request.GET.get('page', 1)
    reparaciones = paginator.get_page(page)
    
    return render(request, 'ecommerce/cuenta/reparaciones.html', {
        'reparaciones': reparaciones,
    })


@login_required
def cuenta_reparacion_detail(request, numero):
    """Vista para mostrar el detalle de una reparación."""
    reparacion = get_object_or_404(Reparacion, numero=numero, cliente=request.user.cliente)
    
    return render(request, 'ecommerce/cuenta/reparacion_detalle.html', {
        'reparacion': reparacion,
    })