import django_filters
from inventario.models import Producto
from ventas.models import Venta
from reparaciones.models import Reparacion
from ecommerce.models import Pedido


class ProductoFilter(django_filters.FilterSet):
    """Filtros para el modelo Producto."""
    
    nombre = django_filters.CharFilter(lookup_expr='icontains')
    codigo = django_filters.CharFilter(lookup_expr='icontains')
    descripcion = django_filters.CharFilter(lookup_expr='icontains')
    precio_min = django_filters.NumberFilter(field_name='precio_venta', lookup_expr='gte')
    precio_max = django_filters.NumberFilter(field_name='precio_venta', lookup_expr='lte')
    stock_min = django_filters.NumberFilter(field_name='stock', lookup_expr='gte')
    stock_max = django_filters.NumberFilter(field_name='stock', lookup_expr='lte')
    
    class Meta:
        model = Producto
        fields = ['categoria', 'estado', 'mostrar_en_tienda', 'es_inventariable']


class VentaFilter(django_filters.FilterSet):
    """Filtros para el modelo Venta."""
    
    fecha_inicio = django_filters.DateFilter(field_name='fecha', lookup_expr='gte')
    fecha_fin = django_filters.DateFilter(field_name='fecha', lookup_expr='lte')
    total_min = django_filters.NumberFilter(field_name='total', lookup_expr='gte')
    total_max = django_filters.NumberFilter(field_name='total', lookup_expr='lte')
    
    class Meta:
        model = Venta
        fields = ['estado', 'cliente', 'vendedor']


class ReparacionFilter(django_filters.FilterSet):
    """Filtros para el modelo Reparacion."""
    
    fecha_inicio = django_filters.DateFilter(field_name='fecha_recepcion', lookup_expr='gte')
    fecha_fin = django_filters.DateFilter(field_name='fecha_recepcion', lookup_expr='lte')
    tipo_equipo = django_filters.CharFilter(lookup_expr='icontains')
    marca = django_filters.CharFilter(lookup_expr='icontains')
    modelo = django_filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = Reparacion
        fields = ['estado', 'cliente', 'tecnico']


class PedidoFilter(django_filters.FilterSet):
    """Filtros para el modelo Pedido."""
    
    fecha_inicio = django_filters.DateFilter(field_name='fecha', lookup_expr='gte')
    fecha_fin = django_filters.DateFilter(field_name='fecha', lookup_expr='lte')
    total_min = django_filters.NumberFilter(field_name='total', lookup_expr='gte')
    total_max = django_filters.NumberFilter(field_name='total', lookup_expr='lte')
    
    class Meta:
        model = Pedido
        fields = ['estado', 'cliente']