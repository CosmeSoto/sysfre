from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from fiscal.models import (
    PeriodoFiscal, CuentaContable, AsientoContable, LineaAsiento, Comprobante,
    Retencion, ComprobanteRetencion
)
from core.models import TipoIVA
from fiscal.services.contabilidad_service import ContabilidadService
from .serializers import (
    PeriodoFiscalSerializer, CuentaContableSerializer,
    AsientoContableSerializer, LineaAsientoSerializer, ComprobanteSerializer,
    TipoIVASerializer, RetencionSerializer, ComprobanteRetencionSerializer
)





class PeriodoFiscalViewSet(viewsets.ModelViewSet):
    queryset = PeriodoFiscal.objects.all()
    serializer_class = PeriodoFiscalSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['nombre']
    filterset_fields = ['estado', 'activo']
    ordering_fields = ['fecha_inicio', 'fecha_fin']
    ordering = ['-fecha_inicio']
    
    @action(detail=True, methods=['post'])
    def cerrar_periodo(self, request, pk=None):
        periodo = self.get_object()
        
        if periodo.estado == 'cerrado':
            return Response(
                {'error': 'El periodo ya está cerrado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        periodo.estado = 'cerrado'
        periodo.save(update_fields=['estado'])
        
        serializer = self.get_serializer(periodo)
        return Response(serializer.data)


class CuentaContableViewSet(viewsets.ModelViewSet):
    queryset = CuentaContable.objects.all()
    serializer_class = CuentaContableSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['codigo', 'nombre', 'descripcion']
    filterset_fields = ['tipo', 'cuenta_padre', 'activo']


class AsientoContableViewSet(viewsets.ModelViewSet):
    queryset = AsientoContable.objects.all()
    serializer_class = AsientoContableSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['numero', 'concepto', 'notas']
    filterset_fields = ['estado', 'tipo', 'periodo_fiscal']
    ordering_fields = ['fecha', 'numero']
    ordering = ['-fecha', '-numero']
    
    @action(detail=False, methods=['post'])
    def crear_asiento(self, request):
        fecha = request.data.get('fecha')
        concepto = request.data.get('concepto')
        lineas = request.data.get('lineas', [])
        tipo = request.data.get('tipo', 'manual')
        periodo_fiscal_id = request.data.get('periodo_fiscal_id')
        
        if not all([fecha, concepto, lineas]):
            return Response(
                {'error': 'Se requieren fecha, concepto y líneas'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(lineas) < 2:
            return Response(
                {'error': 'Se requieren al menos dos líneas'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            asiento = ContabilidadService.crear_asiento(
                fecha=fecha,
                concepto=concepto,
                lineas=lineas,
                tipo=tipo,
                periodo_fiscal_id=periodo_fiscal_id,
                referencia_id=request.data.get('referencia_id'),
                referencia_tipo=request.data.get('referencia_tipo'),
                usuario=request.user
            )
            
            serializer = self.get_serializer(asiento)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def validar(self, request, pk=None):
        asiento = self.get_object()
        
        try:
            asiento = ContabilidadService.validar_asiento(
                asiento=asiento,
                usuario=request.user
            )
            
            serializer = self.get_serializer(asiento)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def anular(self, request, pk=None):
        asiento = self.get_object()
        
        try:
            asiento = ContabilidadService.anular_asiento(
                asiento=asiento,
                usuario=request.user
            )
            
            serializer = self.get_serializer(asiento)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LineaAsientoViewSet(viewsets.ModelViewSet):
    queryset = LineaAsiento.objects.all()
    serializer_class = LineaAsientoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['asiento', 'cuenta']


class ComprobanteViewSet(viewsets.ModelViewSet):
    queryset = Comprobante.objects.all()
    serializer_class = ComprobanteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['numero', 'proveedor__nombre', 'proveedor__ruc']
    filterset_fields = ['tipo', 'estado', 'proveedor']
    ordering_fields = ['fecha_emision', 'total']
    ordering = ['-fecha_emision']


class TipoIVAViewSet(viewsets.ModelViewSet):
    queryset = TipoIVA.objects.all()
    serializer_class = TipoIVASerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['nombre', 'codigo']
    filterset_fields = ['activo', 'es_default']
    
    def perform_create(self, serializer):
        from core.services.iva_service import IVAService
        super().perform_create(serializer)
        IVAService.invalidar_cache()
    
    def perform_update(self, serializer):
        from core.services.iva_service import IVAService
        super().perform_update(serializer)
        IVAService.invalidar_cache()
    
    def perform_destroy(self, instance):
        from core.services.iva_service import IVAService
        super().perform_destroy(instance)
        IVAService.invalidar_cache()


class RetencionViewSet(viewsets.ModelViewSet):
    queryset = Retencion.objects.all()
    serializer_class = RetencionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['nombre', 'codigo']
    filterset_fields = ['tipo', 'activo']


class ComprobanteRetencionViewSet(viewsets.ModelViewSet):
    queryset = ComprobanteRetencion.objects.all()
    serializer_class = ComprobanteRetencionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['numero', 'venta__numero']
    filterset_fields = ['venta']
    ordering_fields = ['fecha_emision']
    ordering = ['-fecha_emision']