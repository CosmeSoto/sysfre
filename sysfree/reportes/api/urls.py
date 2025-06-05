from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReporteViewSet, ProgramacionReporteViewSet, HistorialReporteViewSet

router = DefaultRouter()
router.register(r'reportes', ReporteViewSet)
router.register(r'programaciones', ProgramacionReporteViewSet)
router.register(r'historial', HistorialReporteViewSet)

urlpatterns = [
    path('', include(router.urls)),
]