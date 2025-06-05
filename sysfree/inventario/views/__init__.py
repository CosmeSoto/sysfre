from django.http import HttpResponse

# Placeholder views for the 'inventario' app

def producto_list(request):
    return HttpResponse("Placeholder for producto_list")

def producto_create(request):
    return HttpResponse("Placeholder for producto_create")

def producto_detail(request, pk):
    return HttpResponse(f"Placeholder for producto_detail {pk}")

def producto_update(request, pk):
    return HttpResponse(f"Placeholder for producto_update {pk}")

def producto_delete(request, pk):
    return HttpResponse(f"Placeholder for producto_delete {pk}")

def entrada_inventario(request, pk):
    return HttpResponse(f"Placeholder for entrada_inventario for product {pk}")

def salida_inventario(request, pk):
    return HttpResponse(f"Placeholder for salida_inventario for product {pk}")

def categoria_list(request):
    return HttpResponse("Placeholder for categoria_list")

def categoria_create(request):
    return HttpResponse("Placeholder for categoria_create")

def categoria_update(request, pk):
    return HttpResponse(f"Placeholder for categoria_update {pk}")

def proveedor_list(request):
    return HttpResponse("Placeholder for proveedor_list")

def proveedor_create(request):
    return HttpResponse("Placeholder for proveedor_create")

def proveedor_detail(request, pk):
    return HttpResponse(f"Placeholder for proveedor_detail {pk}")

def proveedor_update(request, pk):
    return HttpResponse(f"Placeholder for proveedor_update {pk}")

def movimiento_list(request):
    return HttpResponse("Placeholder for movimiento_list")