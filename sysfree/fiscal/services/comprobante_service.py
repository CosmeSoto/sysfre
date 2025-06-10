"""
Servicio para gestionar comprobantes fiscales.
"""
from django.db import transaction
from django.utils import timezone
from core.services import IVAService
from ..models import Comprobante


class ComprobanteService:
    """Servicio para gestionar comprobantes fiscales."""
    
    @classmethod
    @transaction.atomic
    def crear_comprobante(cls, numero, tipo, fecha_emision, proveedor, subtotal, 
                         items_iva=None, usuario=None):
        """
        Crea un comprobante fiscal.
        
        Args:
            numero: Número del comprobante
            tipo: Tipo de comprobante
            fecha_emision: Fecha de emisión
            proveedor: Proveedor
            subtotal: Subtotal
            items_iva: Lista de diccionarios con base_imponible y tipo_iva_id
            usuario: Usuario que crea el comprobante
            
        Returns:
            Comprobante: Comprobante creado
        """
        # Calcular impuestos usando el servicio IVA
        impuestos = 0
        if items_iva:
            for item in items_iva:
                base_imponible = item.get('base_imponible', 0)
                tipo_iva = None
                
                if 'tipo_iva_id' in item:
                    tipo_iva = IVAService.get_by_id(item['tipo_iva_id'])
                
                monto_iva, _ = IVAService.calcular_iva(base_imponible, tipo_iva)
                impuestos += monto_iva
        
        # Crear el comprobante
        comprobante = Comprobante(
            numero=numero,
            tipo=tipo,
            fecha_emision=fecha_emision,
            proveedor=proveedor,
            subtotal=subtotal,
            impuestos=impuestos,
            total=subtotal + impuestos,
            estado='borrador'
        )
        
        if usuario:
            comprobante.creado_por = usuario
            comprobante.modificado_por = usuario
        
        comprobante.save()
        return comprobante
    
    @classmethod
    def emitir_comprobante(cls, comprobante, usuario=None):
        """
        Emite un comprobante fiscal.
        
        Args:
            comprobante: Comprobante a emitir
            usuario: Usuario que emite el comprobante
            
        Returns:
            Comprobante: Comprobante emitido
        """
        if comprobante.estado != 'borrador':
            return comprobante
        
        comprobante.estado = 'emitido'
        
        if usuario:
            comprobante.modificado_por = usuario
        
        comprobante.save(update_fields=['estado', 'modificado_por'])
        return comprobante
    
    @classmethod
    def anular_comprobante(cls, comprobante, usuario=None):
        """
        Anula un comprobante fiscal.
        
        Args:
            comprobante: Comprobante a anular
            usuario: Usuario que anula el comprobante
            
        Returns:
            Comprobante: Comprobante anulado
        """
        if comprobante.estado == 'anulado':
            return comprobante
        
        comprobante.estado = 'anulado'
        
        if usuario:
            comprobante.modificado_por = usuario
        
        comprobante.save(update_fields=['estado', 'modificado_por'])
        return comprobante