from django.db import transaction
from django.utils import timezone
from ..models import AsientoContable, LineaAsiento, PeriodoFiscal, CuentaContable
from core.services.auditoria_service import AuditoriaService


class ContabilidadService:
    """Servicio para gestionar operaciones contables."""
    
    @classmethod
    @transaction.atomic
    def crear_asiento(cls, fecha, concepto, lineas, tipo='manual', periodo_fiscal=None, 
                     referencia_id=None, referencia_tipo=None, usuario=None):
        """
        Crea un asiento contable con sus líneas.
        
        Args:
            fecha: Fecha del asiento
            concepto: Concepto del asiento
            lineas: Lista de diccionarios con las líneas del asiento (cuenta_id, descripcion, debe, haber)
            tipo: Tipo de asiento
            periodo_fiscal: Periodo fiscal del asiento (si es None, se busca el periodo activo)
            referencia_id: ID de la referencia
            referencia_tipo: Tipo de referencia
            usuario: Usuario que crea el asiento
            
        Returns:
            AsientoContable: Asiento creado
        """
        # Si no se especifica periodo fiscal, buscar el periodo activo
        if not periodo_fiscal:
            periodo_fiscal = cls.obtener_periodo_activo(fecha)
            if not periodo_fiscal:
                raise ValueError(f"No hay un periodo fiscal activo para la fecha {fecha}")
        
        # Crear el asiento
        asiento = AsientoContable(
            fecha=fecha,
            periodo_fiscal=periodo_fiscal,
            tipo=tipo,
            concepto=concepto,
            referencia_id=referencia_id,
            referencia_tipo=referencia_tipo,
            estado='borrador'
        )
        
        if usuario:
            asiento.creado_por = usuario
            asiento.modificado_por = usuario
        
        asiento.save()
        
        # Crear las líneas del asiento
        for linea_data in lineas:
            cuenta = CuentaContable.objects.get(pk=linea_data['cuenta_id'])
            
            linea = LineaAsiento(
                asiento=asiento,
                cuenta=cuenta,
                descripcion=linea_data.get('descripcion', ''),
                debe=linea_data.get('debe', 0),
                haber=linea_data.get('haber', 0)
            )
            
            if usuario:
                linea.creado_por = usuario
                linea.modificado_por = usuario
            
            linea.save()
        
        # Registrar auditoría
        AuditoriaService.registrar_actividad_personalizada(
            accion="ASIENTO_CONTABLE_CREADO",
            descripcion=f"Asiento contable creado: {concepto}",
            modelo="AsientoContable",
            objeto_id=asiento.id,
            datos={'concepto': concepto, 'total_lineas': len(lineas)}
        )
        
        return asiento
    
    @classmethod
    def validar_asiento(cls, asiento, usuario=None):
        """
        Valida un asiento contable.
        
        Args:
            asiento: Asiento a validar
            usuario: Usuario que valida el asiento
            
        Returns:
            AsientoContable: Asiento validado
        """
        # Verificar que el asiento esté balanceado
        if not asiento.esta_balanceado:
            raise ValueError("El asiento no está balanceado")
        
        # Verificar que tenga al menos dos líneas
        if asiento.lineas.count() < 2:
            raise ValueError("El asiento debe tener al menos dos líneas")
        
        # Cambiar el estado a validado
        asiento.estado = 'validado'
        
        if usuario:
            asiento.modificado_por = usuario
        
        asiento.save(update_fields=['estado', 'modificado_por'])
        return asiento
    
    @classmethod
    def anular_asiento(cls, asiento, usuario=None):
        """
        Anula un asiento contable.
        
        Args:
            asiento: Asiento a anular
            usuario: Usuario que anula el asiento
            
        Returns:
            AsientoContable: Asiento anulado
        """
        # Verificar que el asiento no esté ya anulado
        if asiento.estado == 'anulado':
            return asiento
        
        # Cambiar el estado a anulado
        asiento.estado = 'anulado'
        
        if usuario:
            asiento.modificado_por = usuario
        
        asiento.save(update_fields=['estado', 'modificado_por'])
        return asiento
    
    @classmethod
    def obtener_periodo_activo(cls, fecha=None):
        """
        Obtiene el periodo fiscal activo para una fecha.
        
        Args:
            fecha: Fecha para la que se busca el periodo (si es None, se usa la fecha actual)
            
        Returns:
            PeriodoFiscal: Periodo fiscal activo o None si no hay ninguno
        """
        if fecha is None:
            fecha = timezone.now().date()
        
        try:
            return PeriodoFiscal.objects.get(
                fecha_inicio__lte=fecha,
                fecha_fin__gte=fecha,
                estado='abierto',
                activo=True
            )
        except PeriodoFiscal.DoesNotExist:
            return None