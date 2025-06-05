from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView # Importar directamente

# Importar ViewSets de las aplicaciones específicas
from inventario.api.views import ProductoViewSet, CategoriaViewSet
from clientes.api.views import ClienteViewSet
from ventas.api.views import VentaViewSet
from reparaciones.api.views import ReparacionViewSet
from ecommerce.api.views import PedidoViewSet

app_name = 'api'

# Configuración de Swagger/OpenAPI
schema_view = get_schema_view(
   openapi.Info(
      title="SysFree API",
      default_version='v1',
      description="API para el sistema SysFree",
      terms_of_service="https://www.sysfree.com/terms/",
      contact=openapi.Contact(email="contact@sysfree.com"),
      license=openapi.License(name="Licencia Comercial"),
   ),
   public=True,
   permission_classes=(permissions.IsAuthenticated,),
)

# Crear un router y registrar nuestros viewsets
router = DefaultRouter()
router.register(r'productos', ProductoViewSet, basename='producto')
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'ventas', VentaViewSet, basename='venta')
router.register(r'reparaciones', ReparacionViewSet, basename='reparacion')
router.register(r'pedidos', PedidoViewSet, basename='pedido')

urlpatterns = [
    # API Root
    path('', include(router.urls)),
    
    # Documentación de la API
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Autenticación
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('', include('core.api.urls')), # Comentado para prueba
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # Definición directa
    
    # Incluir las URLs de las aplicaciones específicas
    path('inventario/', include('inventario.api.urls')),
    path('clientes/', include('clientes.api.urls')),
    path('ventas/', include('ventas.api.urls')),
    path('reparaciones/', include('reparaciones.api.urls')),
    path('ecommerce/', include('ecommerce.api.urls')),
    path('fiscal/', include('fiscal.api.urls')),
    path('reportes/', include('reportes.api.urls')),
]