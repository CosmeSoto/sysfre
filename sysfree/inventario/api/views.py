from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from inventario.models import (
    Categoria, Producto, Proveedor, MovimientoInventario, Almacen,
    Lote, StockAlmacen, ContactoProveedor, OrdenCompra, ItemOrdenCompra,
    Variacion, AlertaStock
)
from inventario.services.inventario_service import InventarioService
from inventario.services.stock_notification_service import StockNotificationService
from .serializers import (
    CategoriaSerializer, ProductoSerializer, ProveedorSerializer,
    MovimientoInventarioSerializer, AlmacenSerializer, LoteSerializer,
    StockAlmacenSerializer, ContactoProveedorSerializer, OrdenCompraSerializer,
    ItemOrdenCompraSerializer, VariacionSerializer, AlertaStockSerializer
)

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['nombre', 'descripcion']
    filterset_fields = ['activo']

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['codigo', 'nombre', 'descripcion']
    filterset_fields = ['categoria', 'activo', 'es_inventariable']
    ordering_fields = ['nombre', 'precio_venta', 'stock']
    ordering = ['nombre']
    
    @action(detail=True, methods=['post'])
    def registrar_entrada(self, request, pk=None):
        producto = self.get_object()
        cantidad = request.data.get('cantidad')
        almacen_id = request.data.get('almacen') or request.data.get('almacen_id')
        costo_unitario = request.data.get('costo_unitario')
        origen = request.data.get('origen', 'manual')
        notas = request.data.get('notas', '')
        
        try:
            from inventario.models import Almacen
            almacen = Almacen.objects.get(id=almacen_id) if almacen_id else None
            cantidad = float(cantidad)
            costo_unitario = float(costo_unitario) if costo_unitario else None
            movimiento = InventarioService.registrar_entrada(
                producto=producto,
                cantidad=cantidad,
                origen=origen,
                costo_unitario=costo_unitario,
                notas=notas,
                usuario=request.user,
                almacen=almacen
            )
            
            serializer = MovimientoInventarioSerializer(movimiento)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def registrar_salida(self, request, pk=None):
        producto = self.get_object()
        cantidad = request.data.get('cantidad')
        almacen_id = request.data.get('almacen') or request.data.get('almacen_id')
        origen = request.data.get('origen', 'manual')
        notas = request.data.get('notas', '')
        
        try:
            from inventario.models import Almacen
            almacen = Almacen.objects.get(id=almacen_id) if almacen_id else None
            cantidad = float(cantidad)
            movimiento = InventarioService.registrar_salida(
                producto=producto,
                cantidad=cantidad,
                origen=origen,
                notas=notas,
                usuario=request.user,
                almacen=almacen
            )
            
            serializer = MovimientoInventarioSerializer(movimiento)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['nombre', 'ruc', 'email', 'telefono']
    filterset_fields = ['activo']

class MovimientoInventarioViewSet(viewsets.ModelViewSet):
    queryset = MovimientoInventario.objects.all()
    serializer_class = MovimientoInventarioSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['producto', 'tipo', 'origen', 'almacen']
    ordering_fields = ['fecha']
    ordering = ['-fecha']

class AlmacenViewSet(viewsets.ModelViewSet):
    queryset = Almacen.objects.all()
    serializer_class = AlmacenSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['nombre', 'direccion']
    filterset_fields = ['activo']

class LoteViewSet(viewsets.ModelViewSet):
    queryset = Lote.objects.all()
    serializer_class = LoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['numero', 'notas']
    filterset_fields = ['producto', 'activo']
    ordering_fields = ['fecha_vencimiento']
    ordering = ['fecha_vencimiento']

class StockAlmacenViewSet(viewsets.ModelViewSet):
    queryset = StockAlmacen.objects.all()
    serializer_class = StockAlmacenSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['producto', 'almacen']

class ContactoProveedorViewSet(viewsets.ModelViewSet):
    queryset = ContactoProveedor.objects.all()
    serializer_class = ContactoProveedorSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['nombre', 'cargo', 'email', 'telefono']
    filterset_fields = ['proveedor', 'activo']

class OrdenCompraViewSet(viewsets.ModelViewSet):
    queryset = OrdenCompra.objects.all()
    serializer_class = OrdenCompraSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['numero', 'notas']
    filterset_fields = ['proveedor', 'estado']
    ordering_fields = ['fecha', 'fecha_entrega']
    ordering = ['-fecha']

class ItemOrdenCompraViewSet(viewsets.ModelViewSet):
    queryset = ItemOrdenCompra.objects.all()
    serializer_class = ItemOrdenCompraSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['orden', 'producto']

class VariacionViewSet(viewsets.ModelViewSet):
    queryset = Variacion.objects.all()
    serializer_class = VariacionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['nombre', 'sku']
    filterset_fields = ['producto', 'activo']

class AlertaStockViewSet(viewsets.ModelViewSet):
    queryset = AlertaStock.objects.all()
    serializer_class = AlertaStockSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['producto', 'estado', 'notificado']
    ordering_fields = ['fecha_deteccion', 'fecha_resolucion']
    ordering = ['-fecha_deteccion']
    
    @action(detail=True, methods=['post'])
    def resolver(self, request, pk=None):
        alerta = self.get_object()
        notas = request.data.get('notas', '')
        
        resultado = StockNotificationService.resolver_alerta(alerta.id, notas)
        
        if resultado:
            return Response({'status': 'alerta resuelta'})
        else:
            return Response({'error': 'No se pudo resolver la alerta'}, status=status.HTTP_400_BAD_REQUEST)