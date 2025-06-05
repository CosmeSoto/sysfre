from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q
from ..models import ProductoEcommerce, CategoriaEcommerce


class ProductoListView(ListView):
    """Vista para listar productos en la tienda."""
    model = ProductoEcommerce
    template_name = 'ecommerce/productos/lista.html'
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
            categoria = get_object_or_404(CategoriaEcommerce, slug=categoria_slug)
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


class ProductoDetailView(DetailView):
    """Vista para mostrar el detalle de un producto."""
    model = ProductoEcommerce
    template_name = 'ecommerce/productos/detalle.html'
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
        return context


class CategoriaDetailView(ListView):
    """Vista para mostrar productos de una categoría."""
    model = ProductoEcommerce
    template_name = 'ecommerce/categorias/detalle.html'
    context_object_name = 'productos'
    paginate_by = 12
    
    def get_queryset(self):
        """Filtra los productos por la categoría seleccionada."""
        self.categoria = get_object_or_404(CategoriaEcommerce, slug=self.kwargs['slug'])
        return ProductoEcommerce.objects.filter(
            categorias=self.categoria,
            producto__mostrar_en_tienda=True,
            producto__estado='activo'
        )
    
    def get_context_data(self, **kwargs):
        """Añade datos adicionales al contexto."""
        context = super().get_context_data(**kwargs)
        context['categoria'] = self.categoria
        context['subcategorias'] = CategoriaEcommerce.objects.filter(categoria_padre=self.categoria, activo=True)
        return context