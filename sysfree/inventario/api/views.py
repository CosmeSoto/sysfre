from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from inventario.models import Categoria, Producto, Proveedor, MovimientoInventario, Almacen, StockAlmacen
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
            costo_unitario = float(request.data.get('costo_unitario', 0))
            if cantidad <= 0:
                return Response(
                    {'error': 'La cantidad debe ser mayor que cero'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if costo_unitario <= 0:
                return Response(
                    {'error': 'El costo unitario debe ser mayor que cero'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Obtener almacén
            almacen_id = request.data.get('almacen')
            if not almacen_id:
                return Response(
                    {'error': 'El almacén es obligatorio'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            almacen = Almacen.objects.get(id=almacen_id)
                
            proveedor_id = request.data.get('proveedor')
            proveedor = Proveedor.objects.get(id=proveedor_id) if proveedor_id else None
                
            movimiento = InventarioService.registrar_entrada(
                producto=producto,
                cantidad=cantidad,
                origen=request.data.get('origen', 'compra'),
                costo_unitario=costo_unitario,
                proveedor=proveedor,
                documento=request.data.get('documento', ''),
                notas=request.data.get('notas', ''),
                usuario=request.user,
                almacen=almacen
            )
            
            serializer = MovimientoInventarioSerializer(movimiento)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Proveedor.DoesNotExist:
            return Response(
                {'error': 'Proveedor no encontrado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Almacen.DoesNotExist:
            return Response(
                {'error': 'Almacén no encontrado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
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
                
            # Obtener almacén
            almacen_id = request.data.get('almacen')
            if not almacen_id:
                return Response(
                    {'error': 'El almacén es obligatorio'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            almacen = Almacen.objects.get(id=almacen_id)
                
            # Verificar stock disponible
            stock_almacen = StockAlmacen.objects.filter(producto=producto, almacen=almacen).first()
            if not stock_almacen or stock_almacen.cantidad < cantidad:
                return Response(
                    {'error': 'La cantidad solicitada excede el stock disponible'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            movimiento = InventarioService.registrar_salida(
                producto=producto,
                cantidad=cantidad,
                origen=request.data.get('origen', 'venta'),
                documento=request.data.get('documento', ''),
                notas=request.data.get('notas', ''),
                usuario=request.user,
                almacen=almacen
            )
            
            serializer = MovimientoInventarioSerializer(movimiento)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Almacen.DoesNotExist:
            return Response(
                {'error': 'Almacén no encontrado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


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