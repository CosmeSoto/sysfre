from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.core.cache import cache
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
    
    @method_decorator(cache_page(60 * 30))  # Cache por 30 minutos
    def list(self, request, *args, **kwargs):
        """Lista de categorías con caché de 30 minutos"""
        return super().list(request, *args, **kwargs)
    
    @method_decorator(cache_page(60 * 30))  # Cache por 30 minutos
    def retrieve(self, request, *args, **kwargs):
        """Detalle de categoría con caché de 30 minutos"""
        return super().retrieve(request, *args, **kwargs)


class ProductoEcommerceViewSet(viewsets.ModelViewSet):
    queryset = ProductoEcommerce.objects.all()
    serializer_class = ProductoEcommerceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['producto__nombre', 'producto__codigo', 'slug', 'descripcion_corta', 'descripcion_larga']
    filterset_fields = ['destacado', 'nuevo', 'oferta', 'categorias', 'activo']
    lookup_field = 'slug'
    
    @method_decorator(cache_page(60 * 15))  # Cache por 15 minutos
    def list(self, request, *args, **kwargs):
        """Lista de productos con caché de 15 minutos"""
        return super().list(request, *args, **kwargs)
    
    @method_decorator(cache_page(60 * 15))  # Cache por 15 minutos
    def retrieve(self, request, *args, **kwargs):
        """Detalle de producto con caché de 15 minutos"""
        return super().retrieve(request, *args, **kwargs)
    
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
    
    @method_decorator(cache_page(60 * 30))  # Cache por 30 minutos
    def list(self, request, *args, **kwargs):
        """Lista de imágenes con caché de 30 minutos"""
        return super().list(request, *args, **kwargs)
    
    @method_decorator(cache_page(60 * 30))  # Cache por 30 minutos
    def retrieve(self, request, *args, **kwargs):
        """Detalle de imagen con caché de 30 minutos"""
        return super().retrieve(request, *args, **kwargs)


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
            carrito = CarritoService.obtener_o_crear_carrito(request)
            
            serializer = self.get_serializer(carrito)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def agregar_item(self, request, pk=None):
        carrito = self.get_object()
        producto_id = request.data.get('producto_id')
        cantidad = int(request.data.get('cantidad', 1))
        es_servicio = request.data.get('es_servicio', False)
        
        if not producto_id:
            return Response(
                {'error': 'Se requiere un producto'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            item = CarritoService.agregar_item(
                carrito=carrito,
                item_id=producto_id,
                cantidad=cantidad,
                es_servicio=es_servicio
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
    
    @method_decorator(cache_page(60 * 10))  # Cache por 10 minutos
    @method_decorator(vary_on_cookie)
    def list(self, request, *args, **kwargs):
        """Lista de pedidos con caché de 10 minutos"""
        return super().list(request, *args, **kwargs)
    
    @method_decorator(cache_page(60 * 15))  # Cache por 15 minutos
    @method_decorator(vary_on_cookie)
    def retrieve(self, request, *args, **kwargs):
        """Detalle de pedido con caché de 15 minutos"""
        return super().retrieve(request, *args, **kwargs)
    
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
        
        if not all([carrito_id, direccion_facturacion_id]):
            return Response(
                {'error': 'Se requiere carrito y dirección de facturación'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from clientes.models import DireccionCliente
            from ecommerce.models import Carrito
            
            # Obtener objetos a partir de IDs
            carrito = Carrito.objects.get(id=carrito_id)
            direccion_facturacion = DireccionCliente.objects.get(id=direccion_facturacion_id)
            direccion_envio = DireccionCliente.objects.get(id=direccion_envio_id) if direccion_envio_id else direccion_facturacion
            
            pedido = PedidoService.crear_pedido_desde_carrito(
                carrito=carrito,
                direccion_facturacion=direccion_facturacion,
                direccion_envio=direccion_envio,
                notas=notas
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
        estado = request.data.get('estado', 'completado')
        
        if not all([metodo, monto]):
            return Response(
                {'error': 'Se requiere método y monto'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Crear el pago directamente
            from ecommerce.models import PagoOnline
            
            pago = PagoOnline.objects.create(
                pedido=pedido,
                metodo=metodo,
                monto=float(monto),
                referencia=referencia,
                pasarela_id=pasarela_id,
                estado=estado,
                creado_por=request.user,
                modificado_por=request.user
            )
            
            # Si el pago está completado, actualizar el estado del pedido
            if estado == 'completado':
                PedidoService.actualizar_estado_pedido(pedido, 'pagado')
            
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
            pedido = PedidoService.actualizar_estado_pedido(
                pedido=pedido,
                nuevo_estado=nuevo_estado
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
    
    @method_decorator(cache_page(60 * 15))  # Cache por 15 minutos
    @method_decorator(vary_on_cookie)
    def list(self, request, *args, **kwargs):
        """Lista de pagos con caché de 15 minutos"""
        return super().list(request, *args, **kwargs)
    
    @method_decorator(cache_page(60 * 15))  # Cache por 15 minutos
    @method_decorator(vary_on_cookie)
    def retrieve(self, request, *args, **kwargs):
        """Detalle de pago con caché de 15 minutos"""
        return super().retrieve(request, *args, **kwargs)