from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Reparacion
from ..services.venta_service import ReparacionVentaService

# Placeholder views for reparaciones app
@login_required
def reparacion_list(request):
    return HttpResponse("Lista de reparaciones")

@login_required
def reparacion_create(request):
    return HttpResponse("Crear reparación")

@login_required
def reparacion_detail(request, pk):
    return HttpResponse(f"Detalles de reparación {pk}")

@login_required
def reparacion_edit(request, pk):
    return HttpResponse(f"Editar reparación {pk}")

@login_required
def reparacion_cambiar_estado(request, pk):
    return HttpResponse(f"Cambiar estado de reparación {pk}")

@login_required
def seguimiento_create(request, reparacion_id):
    return HttpResponse(f"Crear seguimiento para reparación {reparacion_id}")

@login_required
def repuesto_create(request, reparacion_id):
    return HttpResponse(f"Agregar repuesto a reparación {reparacion_id}")

@login_required
def repuesto_edit(request, pk):
    return HttpResponse(f"Editar repuesto {pk}")

@login_required
def repuesto_delete(request, pk):
    return HttpResponse(f"Eliminar repuesto {pk}")

@login_required
def reparacion_facturar(request, pk):
    return HttpResponse(f"Facturar reparación {pk}")

@login_required
def reparacion_proforma(request, pk):
    """Vista para generar una proforma para una reparación."""
    reparacion = get_object_or_404(Reparacion, pk=pk)
    
    try:
        # Crear proforma para la reparación
        proforma = ReparacionVentaService.crear_proforma_reparacion(
            reparacion=reparacion,
            usuario=request.user
        )
        
        messages.success(request, f"Proforma {proforma.numero} creada correctamente.")
        return redirect('ventas:proforma_detail', pk=proforma.pk)
    
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('reparaciones:reparacion_detail', pk=pk)

@login_required
def reporte_reparaciones_periodo(request):
    return HttpResponse("Reporte de reparaciones por período")

@login_required
def reporte_reparaciones_tecnico(request):
    return HttpResponse("Reporte de reparaciones por técnico")

@login_required
def reporte_reparaciones_estado(request):
    return HttpResponse("Reporte de reparaciones por estado")

@login_required
def imprimir_orden(request, pk):
    return HttpResponse(f"Imprimir orden de reparación {pk}")

@login_required
def imprimir_recibo(request, pk):
    return HttpResponse(f"Imprimir recibo de reparación {pk}")