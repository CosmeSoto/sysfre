from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Categoria, Producto, Proveedor


class CategoriaForm(forms.ModelForm):
    """Formulario para categorías."""
    
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion', 'codigo', 'imagen', 'categoria_padre', 'orden', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
            'categoria_padre': forms.Select(attrs={'class': 'form-select'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ProductoForm(forms.ModelForm):
    """Formulario para productos."""
    
    class Meta:
        model = Producto
        fields = [
            'codigo', 'nombre', 'descripcion', 'precio_compra', 'precio_venta',
            'stock', 'stock_minimo', 'categoria', 'imagen', 'estado', 'tipo',
            'iva', 'es_inventariable', 'activo'
        ]
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'precio_compra': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'iva': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'es_inventariable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ProveedorForm(forms.ModelForm):
    """Formulario para proveedores."""
    
    class Meta:
        model = Proveedor
        fields = [
            'nombre', 'ruc', 'direccion', 'telefono', 'email', 'sitio_web',
            'contacto_nombre', 'contacto_telefono', 'contacto_email',
            'dias_credito', 'limite_credito', 'activo'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'ruc': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'sitio_web': forms.URLInput(attrs={'class': 'form-control'}),
            'contacto_nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'contacto_telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'contacto_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'dias_credito': forms.NumberInput(attrs={'class': 'form-control'}),
            'limite_credito': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class MovimientoEntradaForm(forms.Form):
    """Formulario para registrar entradas de inventario."""
    
    cantidad = forms.DecimalField(
        label=_('Cantidad'),
        min_value=0.01,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    origen = forms.ChoiceField(
        label=_('Origen'),
        choices=[
            ('compra', _('Compra')),
            ('devolucion', _('Devolución')),
            ('ajuste', _('Ajuste')),
            ('inicial', _('Inventario Inicial')),
            ('otro', _('Otro')),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    costo_unitario = forms.DecimalField(
        label=_('Costo Unitario'),
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    proveedor = forms.ModelChoiceField(
        label=_('Proveedor'),
        queryset=Proveedor.objects.filter(activo=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    documento = forms.CharField(
        label=_('Documento'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    notas = forms.CharField(
        label=_('Notas'),
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )


class MovimientoSalidaForm(forms.Form):
    """Formulario para registrar salidas de inventario."""
    
    cantidad = forms.DecimalField(
        label=_('Cantidad'),
        min_value=0.01,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    origen = forms.ChoiceField(
        label=_('Origen'),
        choices=[
            ('venta', _('Venta')),
            ('devolucion', _('Devolución a Proveedor')),
            ('ajuste', _('Ajuste')),
            ('merma', _('Merma')),
            ('otro', _('Otro')),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    documento = forms.CharField(
        label=_('Documento'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    notas = forms.CharField(
        label=_('Notas'),
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )