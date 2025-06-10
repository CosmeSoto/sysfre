from rest_framework import serializers
from fiscal.models import PeriodoFiscal, CuentaContable, AsientoContable, LineaAsiento, Comprobante


class PeriodoFiscalSerializer(serializers.ModelSerializer):
    esta_activo = serializers.ReadOnlyField()
    
    class Meta:
        model = PeriodoFiscal
        fields = ['id', 'nombre', 'fecha_inicio', 'fecha_fin', 'estado', 'notas', 'esta_activo', 'activo']


class CuentaContableSerializer(serializers.ModelSerializer):
    ruta_completa = serializers.ReadOnlyField()
    
    class Meta:
        model = CuentaContable
        fields = ['id', 'codigo', 'nombre', 'tipo', 'cuenta_padre', 'descripcion', 'ruta_completa', 'activo']


class LineaAsientoSerializer(serializers.ModelSerializer):
    cuenta_nombre = serializers.ReadOnlyField(source='cuenta.nombre')
    
    class Meta:
        model = LineaAsiento
        fields = ['id', 'asiento', 'cuenta', 'cuenta_nombre', 'descripcion', 'debe', 'haber', 'activo']


class AsientoContableSerializer(serializers.ModelSerializer):
    lineas = LineaAsientoSerializer(many=True, read_only=True)
    total_debe = serializers.ReadOnlyField()
    total_haber = serializers.ReadOnlyField()
    esta_balanceado = serializers.ReadOnlyField()
    periodo_fiscal_nombre = serializers.ReadOnlyField(source='periodo_fiscal.nombre')
    
    class Meta:
        model = AsientoContable
        fields = [
            'id', 'numero', 'fecha', 'periodo_fiscal', 'periodo_fiscal_nombre',
            'tipo', 'concepto', 'estado', 'notas', 'referencia_id', 'referencia_tipo',
            'lineas', 'total_debe', 'total_haber', 'esta_balanceado', 'activo'
        ]
        read_only_fields = ['numero']


class ComprobanteSerializer(serializers.ModelSerializer):
    proveedor_nombre = serializers.ReadOnlyField(source='proveedor.nombre')
    
    class Meta:
        model = Comprobante
        fields = [
            'id', 'numero', 'tipo', 'fecha_emision', 'proveedor', 'proveedor_nombre',
            'subtotal', 'impuestos', 'total', 'estado', 'comprobante_relacionado',
            'asiento_contable', 'activo'
        ]