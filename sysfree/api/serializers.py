from rest_framework import serializers
from inventario.models import Producto, Categoria
from clientes.models import Cliente
from ventas.models import Venta, DetalleVenta
from reparaciones.models import Reparacion, SeguimientoReparacion
from ecommerce.models import Pedido, DetallePedido


class CategoriaSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Categoria."""
    
    class Meta:
        model = Categoria
        fields = '__all__'


class ProductoSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Producto."""
    
    categoria_nombre = serializers.ReadOnlyField(source='categoria.nombre')
    
    class Meta:
        model = Producto
        fields = '__all__'


class ProductoDetalleSerializer(serializers.ModelSerializer):
    """Serializador detallado para el modelo Producto."""
    
    categoria = CategoriaSerializer(read_only=True)
    
    class Meta:
        model = Producto
        fields = '__all__'


class ClienteSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Cliente."""
    
    class Meta:
        model = Cliente
        fields = '__all__'


class DetalleVentaSerializer(serializers.ModelSerializer):
    """Serializador para el modelo DetalleVenta."""
    
    producto_nombre = serializers.ReadOnlyField(source='producto.nombre')
    
    class Meta:
        model = DetalleVenta
        fields = '__all__'


class VentaSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Venta."""
    
    cliente_nombre = serializers.ReadOnlyField(source='cliente.nombre')
    detalles = DetalleVentaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Venta
        fields = '__all__'


class SeguimientoReparacionSerializer(serializers.ModelSerializer):
    """Serializador para el modelo SeguimientoReparacion."""
    
    class Meta:
        model = SeguimientoReparacion
        fields = '__all__'


class ReparacionSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Reparacion."""
    
    cliente_nombre = serializers.ReadOnlyField(source='cliente.nombre')
    seguimientos = SeguimientoReparacionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Reparacion
        fields = '__all__'


class DetallePedidoSerializer(serializers.ModelSerializer):
    """Serializador para el modelo DetallePedido."""
    
    producto_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = DetallePedido
        fields = '__all__'
    
    def get_producto_nombre(self, obj):
        if obj.es_servicio:
            return obj.item
        return obj.producto.nombre if obj.producto else None


class PedidoSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Pedido."""
    
    cliente_nombre = serializers.ReadOnlyField(source='cliente.nombre')
    detalles = DetallePedidoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Pedido
        fields = '__all__'