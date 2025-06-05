from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from reportes.models import Reporte, ProgramacionReporte, HistorialReporte
from reportes.services.reporte_service import ReporteService
from .serializers import ReporteSerializer, ProgramacionReporteSerializer, HistorialReporteSerializer


class ReporteViewSet(viewsets.ModelViewSet):
    queryset = Reporte.objects.all()
    serializer_class = ReporteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['nombre', 'descripcion']
    filterset_fields = ['tipo', 'formato', 'es_publico', 'activo']
    
    @action(detail=True, methods=['post'])
    def ejecutar(self, request, pk=None):
        reporte = self.get_object()
        parametros = request.data.get('parametros', {})
        
        try:
            historial = ReporteService.ejecutar_reporte(
                reporte=reporte,
                parametros=parametros,
                usuario=request.user
            )
            
            serializer = HistorialReporteSerializer(historial)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ProgramacionReporteViewSet(viewsets.ModelViewSet):
    queryset = ProgramacionReporte.objects.all()
    serializer_class = ProgramacionReporteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['nombre', 'reporte__nombre', 'destinatarios']
    filterset_fields = ['frecuencia', 'reporte', 'activo']
    
    @action(detail=True, methods=['post'])
    def ejecutar_ahora(self, request, pk=None):
        programacion = self.get_object()
        
        try:
            historial = ReporteService.ejecutar_reporte(
                reporte=programacion.reporte,
                parametros=programacion.parametros,
                programacion=programacion,
                usuario=request.user
            )
            
            serializer = HistorialReporteSerializer(historial)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class HistorialReporteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HistorialReporte.objects.all()
    serializer_class = HistorialReporteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['reporte', 'programacion', 'estado']
    ordering_fields = ['fecha_ejecucion', 'duracion']
    ordering = ['-fecha_ejecucion']