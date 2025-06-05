from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from .exceptions import ResourceNotFoundException


class AuditModelMixin:
    """
    Mixin para asignar automáticamente los campos de auditoría.
    """
    
    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user, modificado_por=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(modificado_por=self.request.user)


class MultiSerializerViewSetMixin:
    """
    Mixin para usar diferentes serializadores según la acción.
    """
    serializer_classes = {}
    
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, super().get_serializer_class())


class ExportableViewSetMixin:
    """
    Mixin para añadir funcionalidad de exportación a un ViewSet.
    """
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        Exporta los datos en formato CSV o Excel.
        """
        format = request.query_params.get('format', 'csv')
        queryset = self.filter_queryset(self.get_queryset())
        
        if format == 'csv':
            return self._export_csv(queryset)
        elif format == 'excel':
            return self._export_excel(queryset)
        else:
            return Response(
                {'error': f'Formato no soportado: {format}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _export_csv(self, queryset):
        """
        Exporta los datos en formato CSV.
        """
        # Implementación básica, debe ser sobrescrita
        return Response(
            {'error': 'Exportación CSV no implementada'},
            status=status.HTTP_501_NOT_IMPLEMENTED
        )
    
    def _export_excel(self, queryset):
        """
        Exporta los datos en formato Excel.
        """
        # Implementación básica, debe ser sobrescrita
        return Response(
            {'error': 'Exportación Excel no implementada'},
            status=status.HTTP_501_NOT_IMPLEMENTED
        )


class SafeDestroyModelMixin:
    """
    Mixin para implementar eliminación segura (soft delete).
    """
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not hasattr(instance, 'activo'):
            return super().destroy(request, *args, **kwargs)
        
        instance.activo = False
        instance.modificado_por = request.user
        instance.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class GetObjectOr404Mixin:
    """
    Mixin para obtener un objeto o devolver 404 con mensaje personalizado.
    """
    
    def get_object_or_404(self, queryset=None, **kwargs):
        """
        Obtiene un objeto o lanza una excepción ResourceNotFoundException.
        """
        if queryset is None:
            queryset = self.get_queryset()
            
        try:
            return queryset.get(**kwargs)
        except queryset.model.DoesNotExist:
            model_name = queryset.model._meta.verbose_name
            raise ResourceNotFoundException(f"{model_name} no encontrado.")