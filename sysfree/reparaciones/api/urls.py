from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReparacionViewSet, SeguimientoReparacionViewSet, RepuestoReparacionViewSet
from reparaciones.models import ServicioReparacion
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import ReparacionSerializer, ServicioReparacionSerializer

# Crear un ViewSet para ServicioReparacion
class ServicioReparacionViewSet(viewsets.ModelViewSet):
    queryset = ServicioReparacion.objects.all()
    serializer_class = ServicioReparacionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['nombre', 'descripcion']
    filterset_fields = ['tipo', 'disponible_online', 'activo']

router = DefaultRouter()
# ReparacionViewSet is registered in the main api/urls.py
router.register(r'seguimientos', SeguimientoReparacionViewSet)
router.register(r'repuestos', RepuestoReparacionViewSet)
# ServicioReparacionViewSet is registered in the main api/urls.py

urlpatterns = [
    path('', include(router.urls)),
]