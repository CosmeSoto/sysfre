from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from ..forms import LoginForm, UsuarioCreationForm, UsuarioChangeForm
from ..services.log_service import LogService


class CustomLoginView(LoginView):
    """Vista personalizada para inicio de sesión."""
    
    form_class = LoginForm
    template_name = 'core/auth/login.html'
    
    def form_valid(self, form):
        """Registra el inicio de sesión exitoso."""
        response = super().form_valid(form)
        LogService.seguridad(
            'Inicio de sesión',
            f'El usuario {self.request.user.email} ha iniciado sesión',
            ip=self.request.META.get('REMOTE_ADDR'),
            usuario=self.request.user
        )
        return response


class CustomPasswordChangeView(PasswordChangeView):
    """Vista personalizada para cambio de contraseña."""
    
    template_name = 'core/auth/password_change.html'
    success_url = reverse_lazy('core:password_change_done')
    
    def form_valid(self, form):
        """Registra el cambio de contraseña exitoso."""
        response = super().form_valid(form)
        LogService.seguridad(
            'Cambio de contraseña',
            f'El usuario {self.request.user.email} ha cambiado su contraseña',
            ip=self.request.META.get('REMOTE_ADDR'),
            usuario=self.request.user
        )
        return response


class CustomPasswordResetView(PasswordResetView):
    """Vista personalizada para restablecimiento de contraseña."""
    
    template_name = 'core/auth/password_reset.html'
    email_template_name = 'core/auth/password_reset_email.html'
    subject_template_name = 'core/auth/password_reset_subject.txt'
    success_url = reverse_lazy('core:password_reset_done')


@login_required
def profile_view(request):
    """Vista para el perfil del usuario."""
    
    if request.method == 'POST':
        form = UsuarioChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            LogService.usuario(
                'Actualización de perfil',
                f'El usuario {request.user.email} ha actualizado su perfil',
                ip=request.META.get('REMOTE_ADDR'),
                usuario=request.user
            )
            return redirect('core:profile')
    else:
        form = UsuarioChangeForm(instance=request.user)
    
    return render(request, 'core/auth/profile.html', {'form': form})


@require_POST
@login_required
def logout_view(request):
    """Vista para cerrar sesión."""
    
    user = request.user
    ip = request.META.get('REMOTE_ADDR')
    
    LogService.seguridad(
        'Cierre de sesión',
        f'El usuario {user.email} ha cerrado sesión',
        ip=ip,
        usuario=user
    )
    
    logout(request)
    return redirect('core:login')