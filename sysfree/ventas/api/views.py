from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from ventas.models import Venta, DetalleVenta, Pago
from ventas.services.venta_service import VentaService
from .serializers import VentaSerializer, DetalleVentaSerializer, PagoSerializer


class VentaViewSet(viewsets.ModelViewSet):
    queryset = Venta.objects.all()
    serializer_class = VentaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['numero', 'cliente__nombres', 'cliente__apellidos', 'cliente__nombre_comercial']
    filterset_fields = ['estado', 'tipo', 'cliente']
    ordering_fields = ['fecha', 'total']
    ordering = ['-fecha']
    
    @action(detail=False, methods=['post'])
    def crear_venta(self, request):
        cliente_id = request.data.get('cliente_id')
        tipo = request.data.get('tipo', 'factura')
        items = request.data.get('items', [])
        direccion_facturacion_id = request.data.get('direccion_facturacion_id')
        direccion_envio_id = request.data.get('direccion_envio_id')
        notas = request.data.get('notas', '')
        
        if not cliente_id:
            return Response(
                {'error': 'Se requiere un cliente'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not items:
            return Response(
                {'error': 'Se requiere al menos un producto'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            venta = VentaService.crear_venta(
                cliente_id=cliente_id,
                tipo=tipo,
                items=items,
                direccion_facturacion_id=direccion_facturacion_id,
                direccion_envio_id=direccion_envio_id,
                notas=notas,
                usuario=request.user
            )
            
            serializer = self.get_serializer(venta)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def registrar_pago(self, request, pk=None):
        venta = self.get_object()
        
        metodo = request.data.get('metodo')
        monto = request.data.get('monto')
        referencia = request.data.get('referencia', '')
        
        if not metodo or not monto:
            return Response(
                {'error': 'Se requiere método de pago y monto'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            pago = VentaService.registrar_pago(
                venta=venta,
                metodo=metodo,
                monto=float(monto),
                referencia=referencia,
                datos_adicionales=request.data,
                usuario=request.user
            )
            
            serializer = PagoSerializer(pago)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        venta = self.get_object()
        nuevo_estado = request.data.get('estado')
        
        if not nuevo_estado:
            return Response(
                {'error': 'Se requiere un estado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            venta = VentaService.cambiar_estado_venta(
                venta=venta,
                nuevo_estado=nuevo_estado,
                usuario=request.user
            )
            
            serializer = self.get_serializer(venta)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DetalleVentaViewSet(viewsets.ModelViewSet):
    queryset = DetalleVenta.objects.all()
    serializer_class = DetalleVentaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['venta', 'producto']


class PagoViewSet(viewsets.ModelViewSet):
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['venta', 'metodo', 'estado']
    ordering_fields = ['fecha', 'monto']
    ordering = ['-fecha']