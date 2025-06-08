from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ventas.models import Venta, Pago
from ventas.services.venta_service import VentaService
from clientes.models import Cliente
from inventario.models import Producto
from django.forms import modelformset_factory
from django.db import transaction
from django.http import HttpResponse

@login_required
def venta_list(request):
    """Lista todas las ventas, incluyendo proformas."""
    ventas = Venta.objects.all().select_related('cliente')
    return render(request, 'ventas/venta_list.html', {'ventas': ventas})

@login_required
def venta_create(request):
    """Crea una nueva venta o proforma."""
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id')
        tipo = request.POST.get('tipo')
        items = []
        for key, value in request.POST.items():
            if key.startswith('producto_'):
                index = key.split('_')[1]
                producto_id = value
                cantidad = float(request.POST.get(f'cantidad_{index}', 1))
                precio_unitario = float(request.POST.get(f'precio_unitario_{index}', 0))
                descuento = float(request.POST.get(f'descuento_{index}', 0))
                items.append({
                    'producto_id': producto_id,
                    'cantidad': cantidad,
                    'precio_unitario': precio_unitario,
                    'descuento': descuento
                })
        try:
            with transaction.atomic():
                cliente = get_object_or_404(Cliente, id=cliente_id)
                venta = VentaService.crear_venta(
                    cliente=cliente,
                    tipo=tipo,
                    items=items,
                    usuario=request.user
                )
                messages.success(request, f"{tipo.capitalize()} {venta.numero} creada correctamente.")
                return redirect('ventas:venta_detail', pk=venta.pk)
        except ValueError as e:
            messages.error(request, str(e))
    clientes = Cliente.objects.all()
    productos = Producto.objects.filter(estado='activo')
    return render(request, 'ventas/venta_create.html', {
        'clientes': clientes,
        'productos': productos,
        'tipos': Venta.TIPO_CHOICES
    })

@login_required
def venta_detail(request, pk):
    """Muestra los detalles de una venta o proforma."""
    venta = get_object_or_404(Venta, pk=pk)
    return render(request, 'ventas/venta_detail.html', {'venta': venta})

@login_required
def venta_edit(request, pk):
    """Edita una venta o proforma."""
    venta = get_object_or_404(Venta, pk=pk)
    if request.method == 'POST':
        # Implementar lógica de edición
        messages.info(request, f"Edición de {venta.numero} no implementada aún.")
        return redirect('ventas:venta_detail', pk=venta.pk)
    return render(request, 'ventas/venta_edit.html', {'venta': venta})

@login_required
def venta_anular(request, pk):
    """Anula una venta o proforma."""
    venta = get_object_or_404(Venta, pk=pk)
    if request.method == 'POST':
        if venta.estado not in ['anulada', 'facturada']:
            venta.estado = 'anulada'
            venta.modificado_por = request.user
            venta.save()
            messages.success(request, f"{venta.numero} anulada correctamente.")
        else:
            messages.error(request, f"No se puede anular una {venta.tipo} en estado {venta.estado}.")
        return redirect('ventas:venta_detail', pk=venta.pk)
    return render(request, 'ventas/venta_anular.html', {'venta': venta})

@login_required
def pago_create(request, venta_id):
    """Crea un pago para una venta."""
    venta = get_object_or_404(Venta, id=venta_id)
    if request.method == 'POST':
        metodo = request.POST.get('metodo')
        monto = float(request.POST.get('monto', 0))
        referencia = request.POST.get('referencia', '')
        estado = 'aprobado' if metodo != 'credito' else 'pendiente'
        try:
            with transaction.atomic():
                pago = Pago.objects.create(
                    venta=venta,
                    metodo=metodo,
                    monto=monto,
                    referencia=referencia,
                    estado=estado,
                    creado_por=request.user,
                    modificado_por=request.user
                )
                messages.success(request, f"Pago de {monto} registrado correctamente.")
                return redirect('ventas:venta_detail', pk=venta.pk)
        except ValueError as e:
            messages.error(request, str(e))
    return render(request, 'ventas/pago_create.html', {
        'venta': venta,
        'metodos': Pago.METODO_CHOICES
    })

@login_required
def pago_edit(request, pk):
    """Edita un pago."""
    pago = get_object_or_404(Pago, pk=pk)
    if request.method == 'POST':
        # Implementar lógica de edición
        messages.info(request, f"Edición de pago {pago.id} no implementada aún.")
        return redirect('ventas:venta_detail', pk=pago.venta.pk)
    return render(request, 'ventas/pago_edit.html', {'pago': pago})

@login_required
def pago_anular(request, pk):
    """Anula un pago."""
    pago = get_object_or_404(Pago, pk=pk)
    if request.method == 'POST':
        if pago.estado != 'anulado':
            pago.estado = 'anulado'
            pago.modificado_por = request.user
            pago.save()
            messages.success(request, f"Pago anulado correctamente.")
        else:
            messages.error(request, f"El pago ya está anulado.")
        return redirect('ventas:venta_detail', pk=pago.venta.pk)
    return render(request, 'ventas/pago_anular.html', {'pago': pago})

@login_required
def imprimir_factura(request, pk):
    """Imprime una factura o proforma."""
    venta = get_object_or_404(Venta, pk=pk)
    context = {'venta': venta, 'tipo': 'proforma' if venta.tipo == 'proforma' else 'factura'}
    return render(request, 'ventas/imprimir.html', context)

@login_required
def reporte_ventas_periodo(request):
    """Genera un reporte de ventas por período."""
    return HttpResponse("Reporte de ventas por período")

@login_required
def reporte_ventas_cliente(request):
    """Genera un reporte de ventas por cliente."""
    return HttpResponse("Reporte de ventas por cliente")

@login_required
def reporte_ventas_producto(request):
    """Genera un reporte de ventas por producto."""
    return HttpResponse("Reporte de ventas por producto")