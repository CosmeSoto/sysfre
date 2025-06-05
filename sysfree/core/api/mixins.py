from rest_framework import status
from rest_framework.response import Response


class AuditModelMixin:
    """
    Mixin to automatically set creado_por and modificado_por fields.
    """
    
    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user, modificado_por=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(modificado_por=self.request.user)


class MultiSerializerViewSetMixin:
    """
    Mixin to use different serializers for different actions.
    """
    serializer_classes = {}
    
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, super().get_serializer_class())


class BulkCreateModelMixin:
    """
    Mixin to allow bulk creation of resources.
    """
    
    def bulk_create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_bulk_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def perform_bulk_create(self, serializer):
        serializer.save()