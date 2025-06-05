from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from ..models import ConfiguracionSistema, Empresa, Sucursal
from ..forms import ConfiguracionSistemaForm, EmpresaForm, SucursalForm
from ..services.log_service import LogService


def es_administrador(user):
    """Verifica si el usuario es administrador."""
    return user.is_staff


@login_required
@user_passes_test(es_administrador)
def configuracion_edit_view(request):
    """Vista para editar configuraciones del sistema."""
    
    configuracion = ConfiguracionSistema.objects.first()
    if not configuracion:
        configuracion = ConfiguracionSistema.objects.create()
    
    if request.method == 'POST':
        form = ConfiguracionSistemaForm(request.POST, instance=configuracion)
        if form.is_valid():
            form.save()
            LogService.sistema(
                'Actualización de configuración',
                'Se han actualizado las configuraciones del sistema',
                ip=request.META.get('REMOTE_ADDR'),
                usuario=request.user
            )
            messages.success(request, _('Configuración actualizada correctamente.'))
            return redirect('core:configuracion_edit')
    else:
        form = ConfiguracionSistemaForm(instance=configuracion)
    
    context = {
        'title': _('Configuraciones del Sistema'),
        'form': form,
        'configuracion': configuracion,
    }
    
    return render(request, 'core/configuracion/edit.html', context)


@login_required
@user_passes_test(es_administrador)
def empresa_edit_view(request):
    """Vista para editar datos de la empresa."""
    
    empresa = Empresa.objects.first()
    
    if request.method == 'POST':
        form = EmpresaForm(request.POST, request.FILES, instance=empresa)
        if form.is_valid():
            form.save()
            LogService.sistema(
                'Actualización de datos de empresa',
                'Se han actualizado los datos de la empresa',
                ip=request.META.get('REMOTE_ADDR'),
                usuario=request.user
            )
            messages.success(request, _('Datos de la empresa actualizados correctamente.'))
            return redirect('core:empresa_edit')
    else:
        form = EmpresaForm(instance=empresa)
    
    context = {
        'title': _('Datos de la Empresa'),
        'form': form,
        'empresa': empresa,
    }
    
    return render(request, 'core/configuracion/empresa.html', context)


@login_required
@user_passes_test(es_administrador)
def sucursal_list_view(request):
    """Vista para listar sucursales."""
    
    sucursales = Sucursal.objects.all().order_by('nombre')
    
    context = {
        'title': _('Sucursales'),
        'sucursales': sucursales,
    }
    
    return render(request, 'core/configuracion/sucursal_list.html', context)


@login_required
@user_passes_test(es_administrador)
def sucursal_create_view(request):
    """Vista para crear una nueva sucursal."""
    
    if request.method == 'POST':
        form = SucursalForm(request.POST)
        if form.is_valid():
            sucursal = form.save()
            LogService.sistema(
                'Creación de sucursal',
                f'Se ha creado la sucursal {sucursal.nombre}',
                ip=request.META.get('REMOTE_ADDR'),
                usuario=request.user
            )
            messages.success(request, _('Sucursal creada correctamente.'))
            return redirect('core:sucursal_list')
    else:
        form = SucursalForm()
    
    context = {
        'title': _('Nueva Sucursal'),
        'form': form,
    }
    
    return render(request, 'core/configuracion/sucursal_form.html', context)


@login_required
@user_passes_test(es_administrador)
def sucursal_edit_view(request, pk):
    """Vista para editar una sucursal."""
    
    sucursal = get_object_or_404(Sucursal, pk=pk)
    
    if request.method == 'POST':
        form = SucursalForm(request.POST, instance=sucursal)
        if form.is_valid():
            form.save()
            LogService.sistema(
                'Actualización de sucursal',
                f'Se ha actualizado la sucursal {sucursal.nombre}',
                ip=request.META.get('REMOTE_ADDR'),
                usuario=request.user
            )
            messages.success(request, _('Sucursal actualizada correctamente.'))
            return redirect('core:sucursal_list')
    else:
        form = SucursalForm(instance=sucursal)
    
    context = {
        'title': _('Editar Sucursal'),
        'form': form,
        'sucursal': sucursal,
    }
    
    return render(request, 'core/configuracion/sucursal_form.html', context)