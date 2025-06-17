from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.core.cache import cache
from clientes.models import Cliente, ContactoCliente, DireccionCliente
from clientes.services.cliente_service import ClienteService
from .serializers import ClienteSerializer, ContactoClienteSerializer, DireccionClienteSerializer


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['identificacion', 'nombres', 'apellidos', 'nombre_comercial', 'email', 'telefono']
    filterset_fields = ['tipo_cliente', 'tipo_identificacion', 'activo']
    
    @method_decorator(cache_page(60 * 15))  # Cache por 15 minutos
    @method_decorator(vary_on_cookie)
    def list(self, request, *args, **kwargs):
        """Lista de clientes con caché de 15 minutos"""
        return super().list(request, *args, **kwargs)
    
    @method_decorator(cache_page(60 * 15))  # Cache por 15 minutos
    @method_decorator(vary_on_cookie)
    def retrieve(self, request, *args, **kwargs):
        """Detalle de cliente con caché de 15 minutos"""
        return super().retrieve(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 5))  # Cache por 5 minutos
    @method_decorator(vary_on_cookie)
    def buscar(self, request):
        termino = request.query_params.get('termino', '')
        if not termino:
            return Response(
                {'error': 'Se requiere un término de búsqueda'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Intentar obtener del caché primero
        cache_key = f'cliente_buscar_{termino}'
        cached_result = cache.get(cache_key)
        
        if cached_result is not None:
            return Response(cached_result)
        
        clientes = ClienteService.buscar_clientes(termino)
        serializer = self.get_serializer(clientes, many=True)
        
        # Guardar en caché
        cache.set(cache_key, serializer.data, 60 * 5)  # 5 minutos
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def agregar_contacto(self, request, pk=None):
        cliente = self.get_object()
        
        serializer = ContactoClienteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(cliente=cliente, creado_por=request.user, modificado_por=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def agregar_direccion(self, request, pk=None):
        cliente = self.get_object()
        
        serializer = DireccionClienteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(cliente=cliente, creado_por=request.user, modificado_por=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContactoClienteViewSet(viewsets.ModelViewSet):
    queryset = ContactoCliente.objects.all()
    serializer_class = ContactoClienteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['cliente', 'es_principal', 'activo']
    search_fields = ['nombres', 'apellidos', 'email', 'telefono']
    
    @method_decorator(cache_page(60 * 15))  # Cache por 15 minutos
    @method_decorator(vary_on_cookie)
    def list(self, request, *args, **kwargs):
        """Lista de contactos con caché de 15 minutos"""
        return super().list(request, *args, **kwargs)
    
    @method_decorator(cache_page(60 * 15))  # Cache por 15 minutos
    @method_decorator(vary_on_cookie)
    def retrieve(self, request, *args, **kwargs):
        """Detalle de contacto con caché de 15 minutos"""
        return super().retrieve(request, *args, **kwargs)


class DireccionClienteViewSet(viewsets.ModelViewSet):
    queryset = DireccionCliente.objects.all()
    serializer_class = DireccionClienteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['cliente', 'tipo', 'es_principal', 'activo']
    search_fields = ['nombre', 'direccion', 'ciudad', 'provincia']
    
    @method_decorator(cache_page(60 * 15))  # Cache por 15 minutos
    @method_decorator(vary_on_cookie)
    def list(self, request, *args, **kwargs):
        """Lista de direcciones con caché de 15 minutos"""
        return super().list(request, *args, **kwargs)
    
    @method_decorator(cache_page(60 * 15))  # Cache por 15 minutos
    @method_decorator(vary_on_cookie)
    def retrieve(self, request, *args, **kwargs):
        """Detalle de dirección con caché de 15 minutos"""
        return super().retrieve(request, *args, **kwargs)