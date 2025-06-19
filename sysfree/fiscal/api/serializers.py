from rest_framework import serializers
from fiscal.models import (
    PeriodoFiscal, CuentaContable, AsientoContable, LineaAsiento, Comprobante,
    Retencion, ComprobanteRetencion
)
from core.models import TipoIVA


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


class TipoIVASerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoIVA
        fields = ['id', 'nombre', 'codigo', 'porcentaje', 'descripcion', 'es_default', 'activo']


class RetencionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Retencion
        fields = ['id', 'nombre', 'codigo', 'porcentaje', 'tipo', 'activo']


class ComprobanteRetencionSerializer(serializers.ModelSerializer):
    venta_numero = serializers.ReadOnlyField(source='venta.numero')
    
    class Meta:
        model = ComprobanteRetencion
        fields = [
            'id', 'numero', 'fecha_emision', 'venta', 'venta_numero',
            'base_imponible', 'total_retenido', 'activo'
        ]