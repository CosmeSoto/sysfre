from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Venta, Proforma
from .services.proforma_service import ProformaService

# Placeholder views for ventas app
@login_required
def venta_list(request):
    return HttpResponse("Lista de ventas")

@login_required
def venta_create(request):
    return HttpResponse("Crear venta")

@login_required
def venta_detail(request, pk):
    return HttpResponse(f"Detalles de venta {pk}")

@login_required
def venta_edit(request, pk):
    return HttpResponse(f"Editar venta {pk}")

@login_required
def venta_anular(request, pk):
    return HttpResponse(f"Anular venta {pk}")

@login_required
def pago_create(request, venta_id):
    return HttpResponse(f"Crear pago para venta {venta_id}")

@login_required
def pago_edit(request, pk):
    return HttpResponse(f"Editar pago {pk}")

@login_required
def pago_anular(request, pk):
    return HttpResponse(f"Anular pago {pk}")

# Vistas para proformas
@login_required
def proforma_list(request):
    """Vista para listar proformas."""
    return HttpResponse("Lista de proformas")

@login_required
def proforma_create(request):
    """Vista para crear una proforma."""
    return HttpResponse("Crear proforma")

@login_required
def proforma_detail(request, pk):
    """Vista para ver detalles de una proforma."""
    proforma = get_object_or_404(Proforma, pk=pk)
    return HttpResponse(f"Detalles de proforma {proforma.numero}")

@login_required
def proforma_edit(request, pk):
    """Vista para editar una proforma."""
    return HttpResponse(f"Editar proforma {pk}")

@login_required
def proforma_convertir(request, pk):
    """Vista para convertir una proforma en factura."""
    proforma = get_object_or_404(Proforma, pk=pk)
    
    try:
        # Convertir proforma a factura
        venta = ProformaService.convertir_a_factura(
            proforma=proforma,
            tipo='factura',
            usuario=request.user
        )
        
        messages.success(request, f"Proforma {proforma.numero} convertida a factura {venta.numero} correctamente.")
        return redirect('ventas:venta_detail', pk=venta.pk)
    
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('ventas:proforma_detail', pk=pk)

@login_required
def imprimir_factura(request, pk):
    return HttpResponse(f"Imprimir factura {pk}")

@login_required
def imprimir_proforma(request, pk):
    return HttpResponse(f"Imprimir proforma {pk}")

@login_required
def reporte_ventas_periodo(request):
    return HttpResponse("Reporte de ventas por período")

@login_required
def reporte_ventas_cliente(request):
    return HttpResponse("Reporte de ventas por cliente")

@login_required
def reporte_ventas_producto(request):
    return HttpResponse("Reporte de ventas por producto")