from rest_framework import serializers
from inventario.models import Categoria, Producto, Proveedor, MovimientoInventario


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion', 'codigo', 'imagen', 'categoria_padre', 'orden', 'activo']


class ProductoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.ReadOnlyField(source='categoria.nombre')
    
    class Meta:
        model = Producto
        fields = [
            'id', 'codigo', 'nombre', 'descripcion', 'precio_compra', 'precio_venta',
            'stock', 'stock_minimo', 'categoria', 'categoria_nombre', 'imagen',
            'estado', 'tipo', 'iva', 'es_inventariable', 'activo'
        ]


class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = [
            'id', 'nombre', 'ruc', 'direccion', 'telefono', 'email', 'sitio_web',
            'contacto_nombre', 'contacto_telefono', 'contacto_email', 'dias_credito',
            'limite_credito', 'activo'
        ]


class MovimientoInventarioSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.ReadOnlyField(source='producto.nombre')
    proveedor_nombre = serializers.ReadOnlyField(source='proveedor.nombre')
    
    class Meta:
        model = MovimientoInventario
        fields = [
            'id', 'fecha', 'tipo', 'origen', 'producto', 'producto_nombre',
            'cantidad', 'stock_anterior', 'stock_nuevo', 'costo_unitario',
            'proveedor', 'proveedor_nombre', 'documento', 'notas'
        ]
        read_only_fields = ['fecha', 'stock_anterior', 'stock_nuevo']