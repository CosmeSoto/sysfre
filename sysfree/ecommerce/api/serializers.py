from rest_framework import serializers
from ecommerce.models import (
    CategoriaEcommerce, ProductoEcommerce, ImagenProducto,
    Carrito, ItemCarrito, Pedido, DetallePedido, PagoOnline
)


class CategoriaEcommerceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaEcommerce
        fields = [
            'id', 'nombre', 'slug', 'descripcion', 'imagen',
            'categoria_padre', 'orden', 'mostrar_en_menu', 'activo'
        ]


class ImagenProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagenProducto
        fields = [
            'id', 'producto', 'imagen', 'titulo', 'alt',
            'orden', 'es_principal', 'activo'
        ]


class ProductoEcommerceSerializer(serializers.ModelSerializer):
    imagenes = ImagenProductoSerializer(many=True, read_only=True)
    producto_nombre = serializers.ReadOnlyField(source='producto.nombre')
    precio_actual = serializers.ReadOnlyField()
    porcentaje_descuento = serializers.ReadOnlyField()
    
    class Meta:
        model = ProductoEcommerce
        fields = [
            'id', 'producto', 'producto_nombre', 'slug', 'categorias',
            'descripcion_corta', 'descripcion_larga', 'meta_titulo',
            'meta_descripcion', 'meta_keywords', 'destacado', 'nuevo',
            'oferta', 'precio_oferta', 'fecha_inicio_oferta', 'fecha_fin_oferta',
            'orden', 'visitas', 'ventas', 'precio_actual', 'porcentaje_descuento',
            'imagenes', 'activo'
        ]


class ItemCarritoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.ReadOnlyField(source='producto.nombre')
    subtotal = serializers.ReadOnlyField()
    impuestos = serializers.ReadOnlyField()
    total = serializers.ReadOnlyField()
    
    class Meta:
        model = ItemCarrito
        fields = [
            'id', 'carrito', 'producto', 'producto_nombre', 'cantidad',
            'precio_unitario', 'impuesto_unitario', 'subtotal', 'impuestos', 'total'
        ]


class CarritoSerializer(serializers.ModelSerializer):
    items = ItemCarritoSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    subtotal = serializers.ReadOnlyField()
    total_impuestos = serializers.ReadOnlyField()
    total = serializers.ReadOnlyField()
    
    class Meta:
        model = Carrito
        fields = [
            'id', 'cliente', 'sesion_id', 'fecha_creacion', 'fecha_actualizacion',
            'convertido_a_pedido', 'items', 'total_items', 'subtotal',
            'total_impuestos', 'total'
        ]
        read_only_fields = ['fecha_creacion', 'fecha_actualizacion']


class DetallePedidoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.ReadOnlyField(source='producto.nombre')
    
    class Meta:
        model = DetallePedido
        fields = [
            'id', 'pedido', 'producto', 'producto_nombre', 'cantidad',
            'precio_unitario', 'impuesto_unitario', 'subtotal', 'impuestos', 'total'
        ]
        read_only_fields = ['subtotal', 'impuestos', 'total']


class PagoOnlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = PagoOnline
        fields = [
            'id', 'pedido', 'metodo', 'monto', 'fecha', 'estado',
            'referencia', 'pasarela_id', 'pasarela_respuesta'
        ]
        read_only_fields = ['fecha']


class PedidoSerializer(serializers.ModelSerializer):
    detalles = DetallePedidoSerializer(many=True, read_only=True)
    pagos = PagoOnlineSerializer(many=True, read_only=True)
    cliente_nombre = serializers.ReadOnlyField(source='cliente.nombre_completo')
    
    class Meta:
        model = Pedido
        fields = [
            'id', 'numero', 'cliente', 'cliente_nombre', 'carrito',
            'fecha', 'estado', 'direccion_facturacion', 'direccion_envio',
            'subtotal', 'impuestos', 'envio', 'descuento', 'total',
            'notas', 'fecha_pago', 'fecha_envio', 'fecha_entrega',
            'codigo_seguimiento', 'factura', 'detalles', 'pagos'
        ]
        read_only_fields = [
            'numero', 'fecha', 'subtotal', 'impuestos', 'total',
            'fecha_pago', 'fecha_envio', 'fecha_entrega'
        ]