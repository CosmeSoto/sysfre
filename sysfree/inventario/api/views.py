from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from inventario.models import Categoria, Producto, Proveedor, MovimientoInventario
from inventario.services.inventario_service import InventarioService
from .serializers import (
    CategoriaSerializer, ProductoSerializer, 
    ProveedorSerializer, MovimientoInventarioSerializer
)


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['nombre', 'codigo', 'descripcion']
    filterset_fields = ['activo', 'categoria_padre']


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['nombre', 'codigo', 'descripcion']
    filterset_fields = ['categoria', 'estado', 'tipo', 'es_inventariable', 'activo']
    
    @action(detail=True, methods=['post'])
    def registrar_entrada(self, request, pk=None):
        producto = self.get_object()
        
        try:
            cantidad = float(request.data.get('cantidad', 0))
            if cantidad <= 0:
                return Response(
                    {'error': 'La cantidad debe ser mayor que cero'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            movimiento = InventarioService.registrar_entrada(
                producto=producto,
                cantidad=cantidad,
                origen=request.data.get('origen', 'compra'),
                costo_unitario=request.data.get('costo_unitario'),
                proveedor=request.data.get('proveedor'), # Cambiado de proveedor_id a proveedor
                documento=request.data.get('documento', ''),
                notas=request.data.get('notas', ''),
                usuario=request.user
            )
            
            serializer = MovimientoInventarioSerializer(movimiento)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def registrar_salida(self, request, pk=None):
        producto = self.get_object()
        
        try:
            cantidad = float(request.data.get('cantidad', 0))
            if cantidad <= 0:
                return Response(
                    {'error': 'La cantidad debe ser mayor que cero'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            movimiento = InventarioService.registrar_salida(
                producto=producto,
                cantidad=cantidad,
                origen=request.data.get('origen', 'venta'),
                documento=request.data.get('documento', ''),
                notas=request.data.get('notas', ''),
                usuario=request.user
            )
            
            serializer = MovimientoInventarioSerializer(movimiento)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre', 'ruc', 'email', 'contacto_nombre']


class MovimientoInventarioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MovimientoInventario.objects.all()
    serializer_class = MovimientoInventarioSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['tipo', 'origen', 'producto', 'proveedor']
    ordering_fields = ['fecha', 'producto']
    ordering = ['-fecha']