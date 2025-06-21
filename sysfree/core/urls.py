from django.urls import path
from django.contrib.auth import views as auth_views
from .views.dashboard_views import dashboard_view
from .views.configuracion_views import (
    configuracion_edit_view,
    empresa_edit_view,
    sucursal_list_view,
    sucursal_create_view,
    sucursal_edit_view,
    configuracion_list_view,
)
from .views.auth_views import (
    CustomLoginView,
    CustomPasswordChangeView,
    CustomPasswordResetView,
    profile_view,
    logout_view,
)

app_name = 'core'

urlpatterns = [
    # Dashboard
    path('', dashboard_view, name='dashboard'),
    path('home/', dashboard_view, name='home'),
    path('products/', dashboard_view, name='products'),
    path('services/', dashboard_view, name='services'),
    path('wishlist/', dashboard_view, name='wishlist'),
    path('compare/', dashboard_view, name='compare'),
    path('orders/', dashboard_view, name='orders'),
    path('repairs/', dashboard_view, name='repairs'),

    # Autenticación
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('password_change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Configuración
    path('configuracion/list/', configuracion_list_view, name='configuracion_list'),
    path('configuracion/edit/', configuracion_edit_view, name='configuracion_edit'),
    path('empresa/edit/', empresa_edit_view, name='empresa_edit'),
    path('sucursales/', sucursal_list_view, name='sucursal_list'),
    path('sucursales/nueva/', sucursal_create_view, name='sucursal_create'),
    path('sucursales/editar/<int:pk>/', sucursal_edit_view, name='sucursal_edit'),
]