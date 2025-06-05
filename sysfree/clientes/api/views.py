from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
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
    
    @action(detail=False, methods=['get'])
    def buscar(self, request):
        termino = request.query_params.get('termino', '')
        if not termino:
            return Response(
                {'error': 'Se requiere un término de búsqueda'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        clientes = ClienteService.buscar_clientes(termino)
        serializer = self.get_serializer(clientes, many=True)
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


class DireccionClienteViewSet(viewsets.ModelViewSet):
    queryset = DireccionCliente.objects.all()
    serializer_class = DireccionClienteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['cliente', 'tipo', 'es_principal', 'activo']
    search_fields = ['nombre', 'direccion', 'ciudad', 'provincia']