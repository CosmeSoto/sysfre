from django.shortcuts import render
from django.db.models import Count
from ..models import ProductoEcommerce, ServicioEcommerce, CategoriaEcommerce


def home(request):
    """Vista para la página de inicio de la tienda."""
    # Productos destacados
    productos_destacados = ProductoEcommerce.objects.filter(
        destacado=True, 
        producto__mostrar_en_tienda=True,
        producto__estado='activo'
    )[:8]
    
    # Servicios destacados
    servicios_destacados = ServicioEcommerce.objects.filter(
        destacado=True,
        servicio__disponible_online=True
    )[:4]
    
    # Productos nuevos
    productos_nuevos = ProductoEcommerce.objects.filter(
        nuevo=True,
        producto__mostrar_en_tienda=True,
        producto__estado='activo'
    ).order_by('-id')[:8]
    
    # Productos en oferta
    productos_oferta = ProductoEcommerce.objects.filter(
        oferta=True,
        producto__mostrar_en_tienda=True,
        producto__estado='activo'
    )[:8]
    
    # Categorías principales
    categorias = CategoriaEcommerce.objects.filter(
        activo=True,
        padre__isnull=True
    ).annotate(
        num_productos=Count('productos')
    ).filter(num_productos__gt=0)[:6]
    
    context = {
        'productos_destacados': productos_destacados,
        'servicios_destacados': servicios_destacados,
        'productos_nuevos': productos_nuevos,
        'productos_oferta': productos_oferta,
        'categorias': categorias,
    }
    
    return render(request, 'ecommerce/home.html', context)