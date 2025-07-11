from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _
from .models import Usuario, ConfiguracionSistema, Empresa, Sucursal


class LoginForm(AuthenticationForm):
    """Formulario para iniciar sesión."""
    username = forms.EmailField(
        label=_("Correo electrónico"),
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'})
    )
    password = forms.CharField(
        label=_("Contraseña"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )


class UsuarioCreationForm(UserCreationForm):
    """Formulario para crear usuarios."""
    class Meta:
        model = Usuario
        fields = ('email', 'nombres', 'apellidos')
        

class UsuarioChangeForm(UserChangeForm):
    """Formulario para modificar usuarios."""
    class Meta:
        model = Usuario
        fields = ('email', 'nombres', 'apellidos', 'is_active')


class ConfiguracionSistemaForm(forms.ModelForm):
    """Formulario para configuraciones del sistema."""
    class Meta:
        model = ConfiguracionSistema
        fields = ['PREFIJO_FACTURA', 'PREFIJO_PROFORMA', 'PREFIJO_NOTA_VENTA', 'PREFIJO_TICKET',
                 'INICIO_FACTURA', 'INICIO_PROFORMA', 'INICIO_NOTA_VENTA', 'INICIO_TICKET',
                 'tipo_iva_default']
        widgets = {
            'PREFIJO_FACTURA': forms.TextInput(attrs={'class': 'form-control'}),
            'PREFIJO_PROFORMA': forms.TextInput(attrs={'class': 'form-control'}),
            'PREFIJO_NOTA_VENTA': forms.TextInput(attrs={'class': 'form-control'}),
            'PREFIJO_TICKET': forms.TextInput(attrs={'class': 'form-control'}),
            'INICIO_FACTURA': forms.NumberInput(attrs={'class': 'form-control'}),
            'INICIO_PROFORMA': forms.NumberInput(attrs={'class': 'form-control'}),
            'INICIO_NOTA_VENTA': forms.NumberInput(attrs={'class': 'form-control'}),
            'INICIO_TICKET': forms.NumberInput(attrs={'class': 'form-control'}),
            'tipo_iva_default': forms.Select(attrs={'class': 'form-control'}),
        }


class EmpresaForm(forms.ModelForm):
    """Formulario para datos de la empresa."""
    class Meta:
        model = Empresa
        fields = ['nombre', 'nombre_comercial', 'ruc', 'direccion', 'telefono', 'email', 
                 'sitio_web', 'logo', 'regimen_fiscal', 'representante_legal', 'cedula_representante',
                 'ambiente_facturacion', 'ruta_certificado', 'clave_certificado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_comercial': forms.TextInput(attrs={'class': 'form-control'}),
            'ruc': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'sitio_web': forms.URLInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'regimen_fiscal': forms.TextInput(attrs={'class': 'form-control'}),
            'representante_legal': forms.TextInput(attrs={'class': 'form-control'}),
            'cedula_representante': forms.TextInput(attrs={'class': 'form-control'}),
            'ambiente_facturacion': forms.Select(attrs={'class': 'form-control'}),
            'ruta_certificado': forms.TextInput(attrs={'class': 'form-control'}),
            'clave_certificado': forms.PasswordInput(attrs={'class': 'form-control'}),
        }


class SucursalForm(forms.ModelForm):
    """Formulario para sucursales."""
    class Meta:
        model = Sucursal
        fields = ['nombre', 'codigo', 'direccion', 'telefono', 'email', 'es_matriz', 'horario']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'es_matriz': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'horario': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }