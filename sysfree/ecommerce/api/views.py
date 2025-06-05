from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from ecommerce.models import (
    CategoriaEcommerce, ProductoEcommerce, ImagenProducto,
    Carrito, ItemCarrito, Pedido, DetallePedido, PagoOnline
)
from ecommerce.services.carrito_service import CarritoService
from ecommerce.services.pedido_service import PedidoService
from .serializers import (
    CategoriaEcommerceSerializer, ProductoEcommerceSerializer, ImagenProductoSerializer,
    CarritoSerializer, ItemCarritoSerializer, PedidoSerializer,
    DetallePedidoSerializer, PagoOnlineSerializer
)


class CategoriaEcommerceViewSet(viewsets.ModelViewSet):
    queryset = CategoriaEcommerce.objects.all()
    serializer_class = CategoriaEcommerceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['nombre', 'slug', 'descripcion']
    filterset_fields = ['mostrar_en_menu', 'categoria_padre', 'activo']
    lookup_field = 'slug'


class ProductoEcommerceViewSet(viewsets.ModelViewSet):
    queryset = ProductoEcommerce.objects.all()
    serializer_class = ProductoEcommerceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['producto__nombre', 'producto__codigo', 'slug', 'descripcion_corta', 'descripcion_larga']
    filterset_fields = ['destacado', 'nuevo', 'oferta', 'categorias', 'activo']
    lookup_field = 'slug'
    
    @action(detail=True, methods=['post'])
    def registrar_visita(self, request, slug=None):
        producto = self.get_object()
        producto.visitas += 1
        producto.save(update_fields=['visitas'])
        return Response({'status': 'visita registrada'})


class ImagenProductoViewSet(viewsets.ModelViewSet):
    queryset = ImagenProducto.objects.all()
    serializer_class = ImagenProductoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['producto', 'es_principal', 'activo']


class CarritoViewSet(viewsets.ModelViewSet):
    queryset = Carrito.objects.all()
    serializer_class = CarritoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtrar por cliente o sesión
        if self.request.user.is_authenticated:
            queryset = queryset.filter(cliente=self.request.user.cliente)
        else:
            sesion_id = self.request.session.session_key
            if sesion_id:
                queryset = queryset.filter(sesion_id=sesion_id)
            else:
                queryset = queryset.none()
        
        # Filtrar solo carritos activos no convertidos a pedido
        queryset = queryset.filter(convertido_a_pedido=False, activo=True)
        return queryset
    
    @action(detail=False, methods=['get', 'post'])
    def actual(self, request):
        # Obtener o crear carrito para el usuario actual
        try:
            if request.user.is_authenticated and hasattr(request.user, 'cliente'):
                carrito = CarritoService.obtener_o_crear_carrito(cliente=request.user.cliente)
            else:
                sesion_id = request.session.session_key
                if not sesion_id:
                    request.session.save()
                    sesion_id = request.session.session_key
                carrito = CarritoService.obtener_o_crear_carrito(sesion_id=sesion_id)
            
            serializer = self.get_serializer(carrito)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def agregar_item(self, request, pk=None):
        carrito = self.get_object()
        producto_id = request.data.get('producto_id')
        cantidad = int(request.data.get('cantidad', 1))
        
        if not producto_id:
            return Response(
                {'error': 'Se requiere un producto'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            item = CarritoService.agregar_item(
                carrito=carrito,
                producto_id=producto_id,
                cantidad=cantidad
            )
            
            serializer = ItemCarritoSerializer(item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def vaciar(self, request, pk=None):
        carrito = self.get_object()
        CarritoService.vaciar_carrito(carrito)
        return Response({'status': 'carrito vaciado'})


class ItemCarritoViewSet(viewsets.ModelViewSet):
    queryset = ItemCarrito.objects.all()
    serializer_class = ItemCarritoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['carrito', 'producto']
    
    @action(detail=True, methods=['post'])
    def actualizar_cantidad(self, request, pk=None):
        item = self.get_object()
        cantidad = int(request.data.get('cantidad', 1))
        
        if cantidad <= 0:
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        item = CarritoService.actualizar_cantidad(item, cantidad)
        serializer = self.get_serializer(item)
        return Response(serializer.data)


class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['numero', 'cliente__nombres', 'cliente__apellidos', 'cliente__nombre_comercial']
    filterset_fields = ['estado', 'cliente']
    ordering_fields = ['fecha', 'total']
    ordering = ['-fecha']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Si no es staff, solo ver pedidos propios
        if not self.request.user.is_staff and hasattr(self.request.user, 'cliente'):
            queryset = queryset.filter(cliente=self.request.user.cliente)
        return queryset
    
    @action(detail=False, methods=['post'])
    def crear_desde_carrito(self, request):
        carrito_id = request.data.get('carrito_id')
        direccion_facturacion_id = request.data.get('direccion_facturacion_id')
        direccion_envio_id = request.data.get('direccion_envio_id')
        notas = request.data.get('notas', '')
        costo_envio = float(request.data.get('costo_envio', 0))
        descuento = float(request.data.get('descuento', 0))
        
        if not all([carrito_id, direccion_facturacion_id]):
            return Response(
                {'error': 'Se requiere carrito y dirección de facturación'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            pedido = PedidoService.crear_pedido_desde_carrito(
                carrito_id=carrito_id,
                direccion_facturacion_id=direccion_facturacion_id,
                direccion_envio_id=direccion_envio_id,
                notas=notas,
                costo_envio=costo_envio,
                descuento=descuento,
                usuario=request.user
            )
            
            serializer = self.get_serializer(pedido)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def registrar_pago(self, request, pk=None):
        pedido = self.get_object()
        metodo = request.data.get('metodo')
        monto = request.data.get('monto')
        referencia = request.data.get('referencia', '')
        pasarela_id = request.data.get('pasarela_id', '')
        pasarela_respuesta = request.data.get('pasarela_respuesta', {})
        estado = request.data.get('estado', 'pendiente')
        
        if not all([metodo, monto]):
            return Response(
                {'error': 'Se requiere método y monto'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            pago = PedidoService.registrar_pago(
                pedido=pedido,
                metodo=metodo,
                monto=float(monto),
                referencia=referencia,
                pasarela_id=pasarela_id,
                pasarela_respuesta=pasarela_respuesta,
                estado=estado,
                usuario=request.user
            )
            
            serializer = PagoOnlineSerializer(pago)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        pedido = self.get_object()
        nuevo_estado = request.data.get('estado')
        
        if not nuevo_estado:
            return Response(
                {'error': 'Se requiere un estado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            pedido = PedidoService.cambiar_estado_pedido(
                pedido=pedido,
                nuevo_estado=nuevo_estado,
                usuario=request.user
            )
            
            serializer = self.get_serializer(pedido)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PagoOnlineViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PagoOnline.objects.all()
    serializer_class = PagoOnlineSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['pedido', 'metodo', 'estado']
    ordering_fields = ['fecha', 'monto']
    ordering = ['-fecha']