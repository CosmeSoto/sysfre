from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.db.models import Q
from ..models import ProductoEcommerce, CategoriaEcommerce, ServicioEcommerce


def mobile_home(request):
    """Vista para la página de inicio móvil."""
    # Productos destacados
    productos_destacados = ProductoEcommerce.objects.filter(
        destacado=True, 
        producto__mostrar_en_tienda=True,
        producto__estado='activo'
    )[:6]
    
    # Servicios destacados
    servicios_destacados = ServicioEcommerce.objects.filter(
        destacado=True,
        servicio__disponible_online=True
    )[:3]
    
    # Productos en oferta
    productos_oferta = ProductoEcommerce.objects.filter(
        oferta=True,
        producto__mostrar_en_tienda=True,
        producto__estado='activo'
    )[:6]
    
    # Categorías principales
    categorias = CategoriaEcommerce.objects.filter(
        activo=True,
        padre__isnull=True
    )[:6]
    
    context = {
        'productos_destacados': productos_destacados,
        'servicios_destacados': servicios_destacados,
        'productos_oferta': productos_oferta,
        'categorias': categorias,
    }
    
    return render(request, 'ecommerce/mobile/home.html', context)


class MobileProductoListView(ListView):
    """Vista para listar productos en la versión móvil."""
    model = ProductoEcommerce
    template_name = 'ecommerce/mobile/productos_lista.html'
    context_object_name = 'productos'
    paginate_by = 12
    
    def get_queryset(self):
        """Filtra los productos según los parámetros de la URL."""
        queryset = ProductoEcommerce.objects.filter(
            producto__mostrar_en_tienda=True,
            producto__estado='activo'
        )
        
        # Filtrar por categoría
        categoria_slug = self.request.GET.get('categoria')
        if categoria_slug:
            categoria = CategoriaEcommerce.objects.get(slug=categoria_slug)
            queryset = queryset.filter(categorias=categoria)
        
        # Filtrar por búsqueda
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(producto__nombre__icontains=q) | 
                Q(producto__codigo__icontains=q) | 
                Q(descripcion_corta__icontains=q) | 
                Q(descripcion_larga__icontains=q)
            )
        
        # Filtrar por precio
        precio_min = self.request.GET.get('precio_min')
        precio_max = self.request.GET.get('precio_max')
        
        if precio_min:
            queryset = queryset.filter(producto__precio_venta__gte=precio_min)
        if precio_max:
            queryset = queryset.filter(producto__precio_venta__lte=precio_max)
        
        # Filtrar por disponibilidad
        disponible = self.request.GET.get('disponible')
        if disponible:
            queryset = queryset.filter(producto__stock__gt=0)
        
        # Filtrar por oferta
        oferta = self.request.GET.get('oferta')
        if oferta:
            queryset = queryset.filter(oferta=True)
        
        # Ordenar
        orden = self.request.GET.get('orden', 'nombre')
        if orden == 'precio_asc':
            queryset = queryset.order_by('producto__precio_venta')
        elif orden == 'precio_desc':
            queryset = queryset.order_by('-producto__precio_venta')
        elif orden == 'nombre':
            queryset = queryset.order_by('producto__nombre')
        elif orden == 'mas_vendidos':
            queryset = queryset.order_by('-ventas')
        elif orden == 'nuevos':
            queryset = queryset.filter(nuevo=True).order_by('-id')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Añade datos adicionales al contexto."""
        context = super().get_context_data(**kwargs)
        context['categorias'] = CategoriaEcommerce.objects.filter(activo=True)
        context['orden_actual'] = self.request.GET.get('orden', 'nombre')
        return context


class MobileProductoDetailView(DetailView):
    """Vista para mostrar el detalle de un producto en la versión móvil."""
    model = ProductoEcommerce
    template_name = 'ecommerce/mobile/producto_detalle.html'
    context_object_name = 'producto'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        """Añade datos adicionales al contexto."""
        context = super().get_context_data(**kwargs)
        
        # Incrementar contador de visitas
        producto = self.object
        producto.visitas += 1
        producto.save(update_fields=['visitas'])
        
        # Obtener productos relacionados
        categorias = producto.categorias.all()
        productos_relacionados = ProductoEcommerce.objects.filter(
            categorias__in=categorias,
            producto__mostrar_en_tienda=True,
            producto__estado='activo'
        ).exclude(id=producto.id).distinct()[:4]
        
        context['productos_relacionados'] = productos_relacionados
        
        # Obtener valoraciones
        context['valoraciones'] = producto.producto.valoraciones.filter(aprobado=True)[:5]
        
        return context