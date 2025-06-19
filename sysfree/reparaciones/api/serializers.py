from rest_framework import serializers
from reparaciones.models import Reparacion, SeguimientoReparacion, RepuestoReparacion, ServicioReparacion


class SeguimientoReparacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeguimientoReparacion
        fields = [
            'id', 'reparacion', 'fecha', 'estado_anterior', 'estado_nuevo',
            'comentario', 'notificado_cliente', 'fecha_notificacion'
        ]
        read_only_fields = ['fecha']


class RepuestoReparacionSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.ReadOnlyField(source='producto.nombre')
    
    class Meta:
        model = RepuestoReparacion
        fields = [
            'id', 'reparacion', 'producto', 'producto_nombre',
            'cantidad', 'precio_unitario', 'subtotal'
        ]
        read_only_fields = ['subtotal']


class ReparacionSerializer(serializers.ModelSerializer):
    seguimientos = SeguimientoReparacionSerializer(many=True, read_only=True)
    repuestos = RepuestoReparacionSerializer(many=True, read_only=True)
    cliente_nombre = serializers.ReadOnlyField(source='cliente.nombre_completo')
    tecnico_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = Reparacion
        fields = [
            'id', 'numero', 'cliente', 'cliente_nombre', 'fecha_recepcion',
            'fecha_estimada_entrega', 'fecha_entrega', 'tipo_equipo', 'marca',
            'modelo', 'problema_reportado', 'diagnostico', 'estado', 'prioridad',
            'tecnico', 'tecnico_nombre', 'costo_diagnostico', 'costo_reparacion',
            'costo_repuestos', 'total', 'facturado', 'factura', 'seguimientos',
            'repuestos'
        ]
        read_only_fields = [
            'numero', 'fecha_recepcion', 'fecha_entrega',
            'costo_repuestos', 'total'
        ]
    
    def get_tecnico_nombre(self, obj):
        if obj.tecnico:
            return f"{obj.tecnico.nombres} {obj.tecnico.apellidos}"
        return None


class ServicioReparacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicioReparacion
        fields = [
            'id', 'nombre', 'descripcion', 'tipo', 'precio', 'tiempo_estimado',
            'producto', 'requiere_diagnostico_previo', 'disponible_online', 'activo'
        ]