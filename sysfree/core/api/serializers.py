from rest_framework import serializers
from core.models import Usuario, Empresa, Sucursal


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'email', 'nombres', 'apellidos', 'is_active', 'fecha_creacion']
        read_only_fields = ['fecha_creacion']


class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = ['id', 'nombre', 'ruc', 'direccion', 'telefono', 'email', 'sitio_web', 'logo']


class SucursalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sucursal
        fields = ['id', 'empresa', 'nombre', 'codigo', 'direccion', 'telefono', 'email', 'es_principal']