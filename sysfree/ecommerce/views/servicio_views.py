from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.db.models import Q
from ..models import ServicioEcommerce, CategoriaEcommerce


class ServicioListView(ListView):
    """Vista para listar servicios de reparación en la tienda."""
    model = ServicioEcommerce
    template_name = 'ecommerce/servicios/lista.html'
    context_object_name = 'servicios'
    paginate_by = 12
    
    def get_queryset(self):
        """Filtra los servicios según los parámetros de la URL."""
        queryset = ServicioEcommerce.objects.filter(servicio__disponible_online=True)
        
        # Filtrar por categoría
        categoria_slug = self.request.GET.get('categoria')
        if categoria_slug:
            categoria = get_object_or_404(CategoriaEcommerce, slug=categoria_slug)
            queryset = queryset.filter(categorias=categoria)
        
        # Filtrar por tipo de servicio
        tipo = self.request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(servicio__tipo=tipo)
        
        # Filtrar por búsqueda
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(servicio__nombre__icontains=q) | 
                Q(descripcion_corta__icontains=q) | 
                Q(descripcion_larga__icontains=q)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Añade datos adicionales al contexto."""
        context = super().get_context_data(**kwargs)
        context['categorias'] = CategoriaEcommerce.objects.filter(activo=True)
        return context


class ServicioDetailView(DetailView):
    """Vista para mostrar el detalle de un servicio de reparación."""
    model = ServicioEcommerce
    template_name = 'ecommerce/servicios/detalle.html'
    context_object_name = 'servicio'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        """Añade datos adicionales al contexto."""
        context = super().get_context_data(**kwargs)
        
        # Incrementar contador de visitas
        servicio = self.object
        servicio.visitas += 1
        servicio.save(update_fields=['visitas'])
        
        # Obtener servicios relacionados
        categorias = servicio.categorias.all()
        servicios_relacionados = ServicioEcommerce.objects.filter(
            categorias__in=categorias,
            servicio__disponible_online=True
        ).exclude(id=servicio.id).distinct()[:3]
        
        context['servicios_relacionados'] = servicios_relacionados
        return context