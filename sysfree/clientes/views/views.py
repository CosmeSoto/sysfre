from django.http import HttpResponse
from django.views.decorators.cache import cache_page
from django.core.cache import cache

# This is the views.py file for the 'clientes' app.
# Add your view functions or classes here.

@cache_page(60 * 15)  # Cache por 15 minutos
def cliente_list(request):
    return HttpResponse("Placeholder for cliente_list")

def cliente_create(request):
    return HttpResponse("Placeholder for cliente_create")

@cache_page(60 * 15)  # Cache por 15 minutos
def cliente_detail(request, pk):
    # Intentar obtener del caché primero
    cache_key = f'cliente_detail_{pk}'
    cached_result = cache.get(cache_key)
    
    if cached_result is not None:
        return HttpResponse(cached_result)
    
    response = f"Placeholder for cliente_detail {pk}"
    
    # Guardar en caché
    cache.set(cache_key, response, 60 * 15)  # 15 minutos
    
    return HttpResponse(response)

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

@cache_page(60 * 5)  # Cache por 5 minutos
def portal_cliente(request):
    return HttpResponse("Placeholder for portal_cliente")

@cache_page(60 * 5)  # Cache por 5 minutos
def portal_perfil(request):
    return HttpResponse("Placeholder for portal_perfil")

@cache_page(60 * 5)  # Cache por 5 minutos
def portal_direcciones(request):
    return HttpResponse("Placeholder for portal_direcciones")

@cache_page(60 * 5)  # Cache por 5 minutos
def portal_pedidos(request):
    return HttpResponse("Placeholder for portal_pedidos")

@cache_page(60 * 5)  # Cache por 5 minutos
def portal_facturas(request):
    return HttpResponse("Placeholder for portal_facturas")

@cache_page(60 * 5)  # Cache por 5 minutos
def portal_reparaciones(request):
    return HttpResponse("Placeholder for portal_reparaciones")