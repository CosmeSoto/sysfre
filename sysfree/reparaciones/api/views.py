from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from reparaciones.models import Reparacion, SeguimientoReparacion, RepuestoReparacion, ServicioReparacion
from reparaciones.services.reparacion_service import ReparacionService
from .serializers import (
    ReparacionSerializer, SeguimientoReparacionSerializer, RepuestoReparacionSerializer,
    ServicioReparacionSerializer
)


class ReparacionViewSet(viewsets.ModelViewSet):
    queryset = Reparacion.objects.all()
    serializer_class = ReparacionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = [
        'numero', 'cliente__nombres', 'cliente__apellidos', 'cliente__nombre_comercial',
        'tipo_equipo', 'marca', 'modelo'
    ]
    filterset_fields = ['estado', 'prioridad', 'tecnico', 'facturado']
    ordering_fields = ['fecha_recepcion', 'fecha_estimada_entrega', 'prioridad']
    ordering = ['-fecha_recepcion']
    
    @action(detail=False, methods=['post'])
    def crear_reparacion(self, request):
        cliente_id = request.data.get('cliente_id')
        tipo_equipo = request.data.get('tipo_equipo')
        marca = request.data.get('marca')
        modelo = request.data.get('modelo')
        problema_reportado = request.data.get('problema_reportado')
        
        if not all([cliente_id, tipo_equipo, marca, modelo, problema_reportado]):
            return Response(
                {'error': 'Faltan campos requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            reparacion = ReparacionService.crear_reparacion(
                cliente_id=cliente_id,
                tipo_equipo=tipo_equipo,
                marca=marca,
                modelo=modelo,
                problema_reportado=problema_reportado,

                prioridad=request.data.get('prioridad', 'media'),
                tecnico_id=request.data.get('tecnico_id'),
                fecha_estimada_entrega=request.data.get('fecha_estimada_entrega'),
                usuario=request.user
            )
            
            serializer = self.get_serializer(reparacion)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        reparacion = self.get_object()
        nuevo_estado = request.data.get('estado')
        comentario = request.data.get('comentario', '')
        notificar_cliente = request.data.get('notificar_cliente', False)
        
        if not nuevo_estado:
            return Response(
                {'error': 'Se requiere un estado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            reparacion, seguimiento = ReparacionService.cambiar_estado(
                reparacion=reparacion,
                nuevo_estado=nuevo_estado,
                comentario=comentario,
                notificar_cliente=notificar_cliente,
                usuario=request.user
            )
            
            serializer = self.get_serializer(reparacion)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def agregar_servicio(self, request, pk=None):
        reparacion = self.get_object()
        servicio_id = request.data.get('servicio')
        precio = request.data.get('precio')
        notas = request.data.get('notas', '')
        
        if not servicio_id:
            return Response(
                {'error': 'Se requiere un servicio'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from reparaciones.models import DetalleServicio
            servicio = ServicioReparacion.objects.get(id=servicio_id)
            
            detalle = DetalleServicio.objects.create(
                reparacion=reparacion,
                servicio=servicio,
                precio=precio or servicio.precio,
                notas=notas
            )
            
            # Actualizar el costo de reparación
            reparacion.costo_reparacion += detalle.precio
            reparacion.save()
            
            return Response({'status': 'servicio agregado'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def agregar_repuesto(self, request, pk=None):
        reparacion = self.get_object()
        producto_id = request.data.get('producto_id')
        cantidad = request.data.get('cantidad')
        precio_unitario = request.data.get('precio_unitario')
        
        if not all([producto_id, cantidad]):
            return Response(
                {'error': 'Se requiere producto y cantidad'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            repuesto = ReparacionService.agregar_repuesto(
                reparacion=reparacion,
                producto_id=producto_id,
                cantidad=float(cantidad),
                precio_unitario=precio_unitario,
                usuario=request.user
            )
            
            serializer = RepuestoReparacionSerializer(repuesto)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SeguimientoReparacionViewSet(viewsets.ModelViewSet):
    queryset = SeguimientoReparacion.objects.all()
    serializer_class = SeguimientoReparacionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['reparacion', 'estado_nuevo', 'notificado_cliente']
    ordering_fields = ['fecha']
    ordering = ['-fecha']


class RepuestoReparacionViewSet(viewsets.ModelViewSet):
    queryset = RepuestoReparacion.objects.all()
    serializer_class = RepuestoReparacionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['reparacion', 'producto']