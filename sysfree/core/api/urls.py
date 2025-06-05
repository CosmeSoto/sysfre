from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UsuarioViewSet, EmpresaViewSet, SucursalViewSet

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet)
router.register(r'empresas', EmpresaViewSet)
router.register(r'sucursales', SucursalViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Include other app APIs
    path('inventario/', include('inventario.api.urls')),
    path('clientes/', include('clientes.api.urls')),
    path('ventas/', include('ventas.api.urls')),
    path('reparaciones/', include('reparaciones.api.urls')),
    path('fiscal/', include('fiscal.api.urls')),
    path('reportes/', include('reportes.api.urls')),
    path('ecommerce/', include('ecommerce.api.urls')),
]