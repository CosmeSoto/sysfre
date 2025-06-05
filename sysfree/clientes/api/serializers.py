from rest_framework import serializers
from clientes.models import Cliente, ContactoCliente, DireccionCliente


class DireccionClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DireccionCliente
        fields = [
            'id', 'cliente', 'tipo', 'nombre', 'direccion', 'ciudad', 
            'provincia', 'codigo_postal', 'es_principal', 'notas',
            'latitud', 'longitud', 'activo'
        ]


class ContactoClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactoCliente
        fields = [
            'id', 'cliente', 'nombres', 'apellidos', 'cargo', 
            'email', 'telefono', 'celular', 'es_principal', 'notas', 'activo'
        ]


class ClienteSerializer(serializers.ModelSerializer):
    direcciones = DireccionClienteSerializer(many=True, read_only=True)
    contactos = ContactoClienteSerializer(many=True, read_only=True)
    
    class Meta:
        model = Cliente
        fields = [
            'id', 'tipo_identificacion', 'identificacion', 'nombres', 'apellidos',
            'nombre_comercial', 'tipo_cliente', 'email', 'telefono', 'celular',
            'direccion', 'fecha_nacimiento', 'limite_credito', 'dias_credito',
            'recibir_promociones', 'usuario', 'direcciones', 'contactos', 'activo'
        ]
        read_only_fields = ['usuario']