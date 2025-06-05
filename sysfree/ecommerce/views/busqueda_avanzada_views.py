from django.shortcuts import render
from django.db.models import Q
from haystack.query import SearchQuerySet
from haystack.inputs import AutoQuery, Clean
from ..models import ProductoEcommerce, ServicioEcommerce, CategoriaEcommerce


def busqueda_avanzada(request):
    """Vista para la búsqueda avanzada de productos y servicios."""
    query = request.GET.get('q', '')
    categoria = request.GET.get('categoria', '')
    tipo = request.GET.get('tipo', 'todos')
    precio_min = request.GET.get('precio_min', '')
    precio_max = request.GET.get('precio_max', '')
    disponible = request.GET.get('disponible', '')
    oferta = request.GET.get('oferta', '')
    
    # Inicializar resultados vacíos
    productos_results = []
    servicios_results = []
    categorias_results = []
    
    if query:
        # Búsqueda de productos
        productos_sqs = SearchQuerySet().models(ProductoEcommerce).filter(content=AutoQuery(query))
        
        # Aplicar filtros adicionales
        if categoria:
            productos_sqs = productos_sqs.filter(categorias=Clean(categoria))
        
        if precio_min:
            productos_sqs = productos_sqs.filter(precio__gte=float(precio_min))
        
        if precio_max:
            productos_sqs = productos_sqs.filter(precio__lte=float(precio_max))
        
        if disponible:
            productos_sqs = productos_sqs.filter(disponible=True)
        
        if oferta:
            productos_sqs = productos_sqs.filter(oferta=True)
        
        # Convertir resultados de búsqueda a objetos del modelo
        productos_results = [result.object for result in productos_sqs]
        
        # Búsqueda de servicios (solo si el tipo es 'todos' o 'servicios')
        if tipo in ['todos', 'servicios']:
            servicios_sqs = SearchQuerySet().models(ServicioEcommerce).filter(content=AutoQuery(query))
            
            if disponible:
                servicios_sqs = servicios_sqs.filter(disponible=True)
            
            if precio_min:
                servicios_sqs = servicios_sqs.filter(precio__gte=float(precio_min))
            
            if precio_max:
                servicios_sqs = servicios_sqs.filter(precio__lte=float(precio_max))
            
            servicios_results = [result.object for result in servicios_sqs]
        
        # Búsqueda de categorías
        categorias_sqs = SearchQuerySet().models(CategoriaEcommerce).filter(content=AutoQuery(query))
        categorias_results = [result.object for result in categorias_sqs]
    
    # Si no hay resultados de búsqueda o no hay query, usar filtros directos en la base de datos
    if not query:
        productos_qs = ProductoEcommerce.objects.filter(
            producto__mostrar_en_tienda=True,
            producto__estado='activo'
        )
        
        if categoria:
            productos_qs = productos_qs.filter(categorias__slug=categoria)
        
        if precio_min:
            productos_qs = productos_qs.filter(producto__precio_venta__gte=precio_min)
        
        if precio_max:
            productos_qs = productos_qs.filter(producto__precio_venta__lte=precio_max)
        
        if disponible:
            productos_qs = productos_qs.filter(producto__stock__gt=0)
        
        if oferta:
            productos_qs = productos_qs.filter(oferta=True)
        
        productos_results = productos_qs[:20]
        
        if tipo in ['todos', 'servicios']:
            servicios_qs = ServicioEcommerce.objects.filter(servicio__disponible_online=True)
            
            if precio_min:
                servicios_qs = servicios_qs.filter(servicio__precio__gte=precio_min)
            
            if precio_max:
                servicios_qs = servicios_qs.filter(servicio__precio__lte=precio_max)
            
            servicios_results = servicios_qs[:10]
    
    # Obtener todas las categorías para el filtro
    todas_categorias = CategoriaEcommerce.objects.filter(activo=True)
    
    context = {
        'query': query,
        'productos': productos_results[:20],  # Limitar resultados
        'servicios': servicios_results[:10],  # Limitar resultados
        'categorias': categorias_results[:10],  # Limitar resultados
        'total_productos': len(productos_results),
        'total_servicios': len(servicios_results),
        'total_categorias': len(categorias_results),
        'todas_categorias': todas_categorias,
        'categoria_seleccionada': categoria,
        'tipo': tipo,
        'precio_min': precio_min,
        'precio_max': precio_max,
        'disponible': disponible,
        'oferta': oferta,
    }
    
    # Detectar si es móvil para usar la plantilla adecuada
    if getattr(request, 'is_mobile', False):
        return render(request, 'ecommerce/mobile/busqueda_avanzada.html', context)
    
    return render(request, 'ecommerce/busqueda/avanzada.html', context)