from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReparacionViewSet, SeguimientoReparacionViewSet, RepuestoReparacionViewSet

router = DefaultRouter()
# ReparacionViewSet is registered in the main api/urls.py
router.register(r'seguimientos', SeguimientoReparacionViewSet)
router.register(r'repuestos', RepuestoReparacionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]