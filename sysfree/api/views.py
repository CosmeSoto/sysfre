from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count, Avg, F, Q
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from datetime import timedelta

from inventario.models import Producto, Categoria
from clientes.models import Cliente
from ventas.models import Venta
from reparaciones.models import Reparacion
from ecommerce.models import Pedido

from .serializers import (
    ProductoSerializer, ProductoDetalleSerializer, CategoriaSerializer,
    ClienteSerializer, VentaSerializer, ReparacionSerializer, PedidoSerializer
)
from .mixins import AuditModelMixin, MultiSerializerViewSetMixin, ExportableViewSetMixin, SafeDestroyModelMixin
from .decorators import log_api_call, require_params
from .utils import export_queryset_to_csv, export_queryset_to_excel
from .exceptions import BusinessLogicException, ResourceNotFoundException
from core.services.cache_service import CacheService


class ProductoViewSet(AuditModelMixin, MultiSerializerViewSetMixin, ExportableViewSetMixin, SafeDestroyModelMixin, viewsets.ModelViewSet):
    """
    API endpoint para productos.
    
    list:
    Retorna una lista paginada de productos.
    
    create:
    Crea un nuevo producto.
    
    retrieve:
    Retorna los detalles de un producto específico.
    
    update:
    Actualiza un producto completo.
    
    partial_update:
    Actualiza parcialmente un producto.
    
    destroy:
    Elimina un producto (soft delete).
    
    export:
    Exporta la lista de productos en formato CSV o Excel.
    """
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['categoria', 'estado', 'mostrar_en_tienda']
    search_fields = ['nombre', 'codigo', 'descripcion']
    ordering_fields = ['nombre', 'precio_venta', 'stock']
    
    serializer_classes = {
        'retrieve': ProductoDetalleSerializer,
        'list': ProductoSerializer,
    }
    
    def _export_csv(self, queryset):
        """Exporta productos a CSV."""
        fields = ['codigo', 'nombre', 'precio_venta', 'stock', 'categoria']
        return export_queryset_to_csv(queryset, fields, 'productos.csv')
    
    def _export_excel(self, queryset):
        """Exporta productos a Excel."""
        fields = ['codigo', 'nombre', 'precio_venta', 'stock', 'categoria']
        return export_queryset_to_excel(queryset, fields, 'productos.xlsx')


class CategoriaViewSet(AuditModelMixin, SafeDestroyModelMixin, viewsets.ModelViewSet):
    """
    API endpoint para categorías.
    """
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre']


class ClienteViewSet(AuditModelMixin, SafeDestroyModelMixin, viewsets.ModelViewSet):
    """
    API endpoint para clientes.
    """
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['tipo']
    search_fields = ['nombre', 'email', 'telefono', 'identificacion']
    ordering_fields = ['nombre', 'fecha_registro']


class VentaViewSet(AuditModelMixin, SafeDestroyModelMixin, viewsets.ModelViewSet):
    """
    API endpoint para ventas.
    """
    queryset = Venta.objects.all()
    serializer_class = VentaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['estado', 'cliente']
    search_fields = ['numero', 'cliente__nombre']
    ordering_fields = ['fecha', 'total']


class ReparacionViewSet(AuditModelMixin, SafeDestroyModelMixin, viewsets.ModelViewSet):
    """
    API endpoint para reparaciones.
    """
    queryset = Reparacion.objects.all()
    serializer_class = ReparacionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['estado', 'cliente', 'tecnico']
    search_fields = ['numero', 'cliente__nombre', 'tipo_equipo', 'marca', 'modelo']
    ordering_fields = ['fecha_recepcion', 'fecha_estimada_entrega']


class PedidoViewSet(AuditModelMixin, SafeDestroyModelMixin, viewsets.ModelViewSet):
    """
    API endpoint para pedidos online.
    """
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['estado', 'cliente']
    search_fields = ['numero', 'cliente__nombre']
    ordering_fields = ['fecha', 'total']


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@log_api_call
@require_params('q')
def buscar_productos(request):
    """
    Endpoint para buscar productos con filtros avanzados.
    
    Parámetros:
    - q: Texto a buscar (requerido)
    - categoria: ID de la categoría
    - precio_min: Precio mínimo
    - precio_max: Precio máximo
    - disponible: 1 para mostrar solo productos disponibles
    """
    query = request.query_params.get('q', '')
    categoria = request.query_params.get('categoria')
    precio_min = request.query_params.get('precio_min')
    precio_max = request.query_params.get('precio_max')
    disponible = request.query_params.get('disponible')
    
    # Intentar obtener resultados de caché para búsquedas comunes
    cache_key = f"buscar_productos_{query}_{categoria}_{precio_min}_{precio_max}_{disponible}"
    cached_data = CacheService.get(cache_key)
    
    if cached_data:
        return Response(cached_data)
    
    productos = Producto.objects.all()
    
    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) | 
            Q(codigo__icontains=query) | 
            Q(descripcion__icontains=query)
        )
    
    if categoria:
        productos = productos.filter(categoria__id=categoria)
    
    if precio_min:
        productos = productos.filter(precio_venta__gte=precio_min)
    
    if precio_max:
        productos = productos.filter(precio_venta__lte=precio_max)
    
    if disponible:
        productos = productos.filter(stock__gt=0)
    
    serializer = ProductoSerializer(productos, many=True)
    
    # Guardar en caché por 10 minutos
    CacheService.set(cache_key, serializer.data, 600)
    
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@log_api_call
def actualizar_stock(request, pk):
    """
    Endpoint para actualizar el stock de un producto.
    
    Parámetros:
    - cantidad: Cantidad a actualizar (requerido)
    - tipo: 'entrada' o 'salida' (por defecto 'entrada')
    """
    try:
        producto = get_object_or_404(Producto, pk=pk)
        cantidad = request.data.get('cantidad')
        tipo = request.data.get('tipo', 'entrada')  # entrada o salida
        
        if not cantidad:
            raise BusinessLogicException('Se requiere la cantidad')
        
        try:
            cantidad = int(cantidad)
            if cantidad <= 0:
                raise BusinessLogicException('La cantidad debe ser un número positivo')
                
            if tipo == 'entrada':
                producto.stock += cantidad
            else:
                if producto.stock < cantidad:
                    raise BusinessLogicException('Stock insuficiente')
                producto.stock -= cantidad
            
            producto.modificado_por = request.user
            producto.save()
            serializer = ProductoSerializer(producto)
            return Response(serializer.data)
        
        except ValueError:
            raise BusinessLogicException('La cantidad debe ser un número entero')
    
    except Exception as e:
        if isinstance(e, BusinessLogicException):
            raise e
        raise BusinessLogicException(str(e))


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@log_api_call
def actualizar_estado_venta(request, pk):
    """
    Endpoint para actualizar el estado de una venta.
    
    Parámetros:
    - estado: Nuevo estado (requerido)
    """
    venta = get_object_or_404(Venta, pk=pk)
    estado = request.data.get('estado')
    
    if not estado:
        raise BusinessLogicException('Se requiere el estado')
    
    estados_validos = ['pendiente', 'pagado', 'enviado', 'entregado', 'cancelado']
    if estado not in estados_validos:
        raise BusinessLogicException(f'Estado no válido. Debe ser uno de: {", ".join(estados_validos)}')
    
    venta.estado = estado
    venta.modificado_por = request.user
    venta.save()
    serializer = VentaSerializer(venta)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@log_api_call
def actualizar_estado_reparacion(request, pk):
    """
    Endpoint para actualizar el estado de una reparación.
    
    Parámetros:
    - estado: Nuevo estado (requerido)
    - descripcion: Descripción del cambio de estado
    """
    reparacion = get_object_or_404(Reparacion, pk=pk)
    estado = request.data.get('estado')
    descripcion = request.data.get('descripcion', '')
    
    if not estado:
        raise BusinessLogicException('Se requiere el estado')
    
    estados_validos = [
        'recibido', 'diagnostico', 'espera_repuestos', 'en_reparacion',
        'reparado', 'entregado', 'no_reparable', 'cancelado'
    ]
    if estado not in estados_validos:
        raise BusinessLogicException(f'Estado no válido. Debe ser uno de: {", ".join(estados_validos)}')
    
    reparacion.estado = estado
    reparacion.modificado_por = request.user
    reparacion.save()
    
    # Crear seguimiento
    if descripcion:
        reparacion.seguimientos.create(
            estado=estado,
            descripcion=descripcion,
            usuario=request.user,
            creado_por=request.user,
            modificado_por=request.user
        )
    
    serializer = ReparacionSerializer(reparacion)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@log_api_call
def actualizar_estado_pedido(request, pk):
    """
    Endpoint para actualizar el estado de un pedido.
    
    Parámetros:
    - estado: Nuevo estado (requerido)
    """
    pedido = get_object_or_404(Pedido, pk=pk)
    estado = request.data.get('estado')
    
    if not estado:
        raise BusinessLogicException('Se requiere el estado')
    
    estados_validos = ['pendiente', 'pagado', 'enviado', 'entregado', 'cancelado']
    if estado not in estados_validos:
        raise BusinessLogicException(f'Estado no válido. Debe ser uno de: {", ".join(estados_validos)}')
    
    pedido.estado = estado
    pedido.modificado_por = request.user
    pedido.save()
    serializer = PedidoSerializer(pedido)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@log_api_call
def estadisticas_ventas(request):
    """
    Endpoint para obtener estadísticas de ventas.
    """
    # Intentar obtener de caché
    cache_key = "estadisticas_ventas"
    cached_data = CacheService.get(cache_key)
    
    if cached_data:
        return Response(cached_data)
    
    # Fecha actual y hace 30 días
    hoy = timezone.now().date()
    hace_30_dias = hoy - timedelta(days=30)
    
    # Ventas de los últimos 30 días
    ventas_30_dias = Venta.objects.filter(
        fecha__date__gte=hace_30_dias,
        estado__in=['pagado', 'enviado', 'entregado']
    )
    
    # Total de ventas
    total_ventas = ventas_30_dias.aggregate(total=Sum('total'))['total'] or 0
    
    # Número de ventas
    num_ventas = ventas_30_dias.count()
    
    # Ventas por día
    ventas_por_dia = list(ventas_30_dias.values('fecha__date')
                          .annotate(total=Sum('total'), cantidad=Count('id'))
                          .order_by('fecha__date'))
    
    # Ventas por estado
    ventas_por_estado = list(Venta.objects.values('estado')
                            .annotate(cantidad=Count('id'), total=Sum('total'))
                            .order_by('estado'))
    
    data = {
        'total_ventas': total_ventas,
        'num_ventas': num_ventas,
        'ventas_por_dia': ventas_por_dia,
        'ventas_por_estado': ventas_por_estado
    }
    
    # Guardar en caché por 1 hora
    CacheService.set(cache_key, data, 3600)
    
    return Response(data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@log_api_call
def estadisticas_productos(request):
    """
    Endpoint para obtener estadísticas de productos.
    """
    # Intentar obtener de caché
    cache_key = "estadisticas_productos"
    cached_data = CacheService.get(cache_key)
    
    if cached_data:
        return Response(cached_data)
    
    # Productos más vendidos
    productos_mas_vendidos = list(Producto.objects.annotate(
        total_vendido=Sum('detalles_venta__cantidad')
    ).filter(total_vendido__gt=0).order_by('-total_vendido')[:10].values(
        'id', 'nombre', 'total_vendido'
    ))
    
    # Productos con stock bajo
    productos_stock_bajo = list(Producto.objects.filter(
        stock__lte=F('stock_minimo'),
        es_inventariable=True
    ).values('id', 'nombre', 'stock', 'stock_minimo'))
    
    # Productos por categoría
    productos_por_categoria = list(Categoria.objects.annotate(
        cantidad_productos=Count('productos')
    ).values('id', 'nombre', 'cantidad_productos'))
    
    data = {
        'productos_mas_vendidos': productos_mas_vendidos,
        'productos_stock_bajo': productos_stock_bajo,
        'productos_por_categoria': productos_por_categoria
    }
    
    # Guardar en caché por 1 hora
    CacheService.set(cache_key, data, 3600)
    
    return Response(data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@log_api_call
def estadisticas_reparaciones(request):
    """
    Endpoint para obtener estadísticas de reparaciones.
    """
    # Intentar obtener de caché
    cache_key = "estadisticas_reparaciones"
    cached_data = CacheService.get(cache_key)
    
    if cached_data:
        return Response(cached_data)
    
    # Fecha actual y hace 30 días
    hoy = timezone.now().date()
    hace_30_dias = hoy - timedelta(days=30)
    
    # Reparaciones de los últimos 30 días
    reparaciones_30_dias = Reparacion.objects.filter(
        fecha_recepcion__date__gte=hace_30_dias
    )
    
    # Total de reparaciones
    total_reparaciones = reparaciones_30_dias.aggregate(total=Sum('total'))['total'] or 0
    
    # Número de reparaciones
    num_reparaciones = reparaciones_30_dias.count()
    
    # Reparaciones por estado
    reparaciones_por_estado = list(Reparacion.objects.values('estado')
                                  .annotate(cantidad=Count('id'))
                                  .order_by('estado'))
    
    # Tiempo promedio de reparación (en días)
    tiempo_promedio = Reparacion.objects.filter(
        estado='entregado',
        fecha_entrega__isnull=False
    ).annotate(
        tiempo=F('fecha_entrega') - F('fecha_recepcion')
    ).aggregate(promedio=Avg('tiempo'))['promedio']
    
    tiempo_promedio_dias = tiempo_promedio.days if tiempo_promedio else 0
    
    data = {
        'total_reparaciones': total_reparaciones,
        'num_reparaciones': num_reparaciones,
        'reparaciones_por_estado': reparaciones_por_estado,
        'tiempo_promedio_dias': tiempo_promedio_dias
    }
    
    # Guardar en caché por 1 hora
    CacheService.set(cache_key, data, 3600)
    
    return Response(data)