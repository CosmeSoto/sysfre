from rest_framework import serializers
from ventas.models import Venta, DetalleVenta, Pago


class DetalleVentaSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.ReadOnlyField(source='producto.nombre')
    
    class Meta:
        model = DetalleVenta
        fields = [
            'id', 'venta', 'producto', 'producto_nombre', 'cantidad', 
            'precio_unitario', 'descuento', 'iva', 'subtotal', 'total'
        ]
        read_only_fields = ['subtotal', 'total']


class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = [
            'id', 'venta', 'fecha', 'metodo', 'monto', 'referencia', 'estado',
            'numero_tarjeta', 'titular_tarjeta', 'banco', 'numero_cuenta',
            'numero_cheque', 'banco_cheque'
        ]
        read_only_fields = ['fecha']


class VentaSerializer(serializers.ModelSerializer):
    detalles = DetalleVentaSerializer(many=True, read_only=True)
    pagos = PagoSerializer(many=True, read_only=True)
    cliente_nombre = serializers.ReadOnlyField(source='cliente.nombre_completo')
    
    class Meta:
        model = Venta
        fields = [
            'id', 'numero', 'fecha', 'cliente', 'cliente_nombre', 'direccion_facturacion',
            'direccion_envio', 'tipo', 'estado', 'subtotal', 'iva', 'descuento', 'total',
            'notas', 'clave_acceso', 'numero_autorizacion', 'fecha_autorizacion',
            'fecha_pago', 'fecha_envio', 'fecha_entrega', 'detalles', 'pagos'
        ]
        read_only_fields = [
            'numero', 'fecha', 'subtotal', 'iva', 'total',
            'fecha_pago', 'fecha_envio', 'fecha_entrega'
        ]