from django.shortcuts import render
from django.db.models import Q
from ..models import ProductoEcommerce, ServicioEcommerce, CategoriaEcommerce


def buscar(request):
    """Vista para buscar productos y servicios en la tienda."""
    query = request.GET.get('q', '')
    
    if query:
        # Buscar productos
        productos = ProductoEcommerce.objects.filter(
            Q(producto__nombre__icontains=query) |
            Q(producto__codigo__icontains=query) |
            Q(descripcion_corta__icontains=query) |
            Q(descripcion_larga__icontains=query),
            producto__mostrar_en_tienda=True,
            producto__estado='activo'
        )
        
        # Buscar servicios
        servicios = ServicioEcommerce.objects.filter(
            Q(servicio__nombre__icontains=query) |
            Q(descripcion_corta__icontains=query) |
            Q(descripcion_larga__icontains=query),
            servicio__disponible_online=True
        )
        
        # Buscar categorías
        categorias = CategoriaEcommerce.objects.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query),
            activo=True
        )
    else:
        productos = ProductoEcommerce.objects.none()
        servicios = ServicioEcommerce.objects.none()
        categorias = CategoriaEcommerce.objects.none()
    
    context = {
        'query': query,
        'productos': productos[:12],  # Limitar resultados
        'servicios': servicios[:6],   # Limitar resultados
        'categorias': categorias[:6], # Limitar resultados
        'total_productos': productos.count(),
        'total_servicios': servicios.count(),
        'total_categorias': categorias.count(),
    }
    
    return render(request, 'ecommerce/busqueda/resultados.html', context)