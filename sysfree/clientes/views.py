from django.http import HttpResponse

# This is the views.py file for the 'clientes' app.
# Add your view functions or classes here.

def cliente_list(request):
    return HttpResponse("Placeholder for cliente_list")

def cliente_create(request):
    return HttpResponse("Placeholder for cliente_create")

def cliente_detail(request, pk):
    return HttpResponse(f"Placeholder for cliente_detail {pk}")

def cliente_edit(request, pk):
    return HttpResponse(f"Placeholder for cliente_edit {pk}")

def contacto_create(request, cliente_id):
    return HttpResponse(f"Placeholder for contacto_create for cliente {cliente_id}")

def contacto_edit(request, pk):
    return HttpResponse(f"Placeholder for contacto_edit {pk}")

def contacto_delete(request, pk):
    return HttpResponse(f"Placeholder for contacto_delete {pk}")

def direccion_create(request, cliente_id):
    return HttpResponse(f"Placeholder for direccion_create for cliente {cliente_id}")

def direccion_edit(request, pk):
    return HttpResponse(f"Placeholder for direccion_edit {pk}")

def direccion_delete(request, pk):
    return HttpResponse(f"Placeholder for direccion_delete {pk}")

def portal_cliente(request):
    return HttpResponse("Placeholder for portal_cliente")

def portal_perfil(request):
    return HttpResponse("Placeholder for portal_perfil")

def portal_direcciones(request):
    return HttpResponse("Placeholder for portal_direcciones")

def portal_pedidos(request):
    return HttpResponse("Placeholder for portal_pedidos")

def portal_facturas(request):
    return HttpResponse("Placeholder for portal_facturas")

def portal_reparaciones(request):
    return HttpResponse("Placeholder for portal_reparaciones")