from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClienteViewSet, ContactoClienteViewSet, DireccionClienteViewSet

router = DefaultRouter()
# ClienteViewSet is registered in the main api/urls.py
router.register(r'contactos', ContactoClienteViewSet)
router.register(r'direcciones', DireccionClienteViewSet)

urlpatterns = [
    path('', include(router.urls)),
]