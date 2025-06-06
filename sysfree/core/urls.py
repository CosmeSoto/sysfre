from django.urls import path
from django.contrib.auth import views as auth_views
from .views import dashboard_view # Changed to direct import

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]