"""
Ejemplo de uso del servicio IVA en diferentes partes de la aplicación.
Este archivo es solo para fines ilustrativos y no forma parte del código de producción.
"""
from decimal import Decimal
from django.db import models
from core.services import IVAService
from core.models import TipoIVA, ModeloBase


class EjemploFactura(ModeloBase):
    """Modelo de ejemplo para demostrar el uso del IVAService."""
    
    cliente = models.CharField(max_length=100)
    fecha = models.DateField(auto_now_add=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_iva = models.ForeignKey(
        TipoIVA, 
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    monto_iva = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para calcular automáticamente el IVA.
        Si no se especifica un tipo_iva, se usa el predeterminado.
        """
        # Si no se especificó un tipo de IVA, usar el predeterminado
        if not self.tipo_iva:
            self.tipo_iva = IVAService.get_default()
            
        # Calcular el IVA y el total
        self.monto_iva, self.total = IVAService.calcular_iva(
            self.subtotal, 
            self.tipo_iva
        )
        
        super().save(*args, **kwargs)


# Ejemplos de uso en vistas o servicios
def ejemplo_uso_en_vista():
    """Ejemplo de cómo usar IVAService en una vista."""
    # Obtener el IVA predeterminado
    iva_default = IVAService.get_default()
    
    # Obtener un IVA específico por código
    iva_reducido = IVAService.get_by_codigo('REDUCIDO')
    
    # Obtener un IVA por porcentaje
    iva_21 = IVAService.get_by_porcentaje(Decimal('21.00'))
    
    # Calcular IVA para un monto
    base_imponible = Decimal('100.00')
    monto_iva, total = IVAService.calcular_iva(base_imponible)
    
    # Calcular IVA con un tipo específico
    monto_iva_reducido, total_reducido = IVAService.calcular_iva(
        base_imponible, 
        iva_reducido
    )
    
    # Obtener todos los tipos de IVA disponibles
    todos_los_ivas = IVAService.get_all()
    
    return {
        'iva_default': iva_default,
        'iva_reducido': iva_reducido,
        'iva_21': iva_21,
        'calculo_default': {
            'base': base_imponible,
            'iva': monto_iva,
            'total': total
        },
        'calculo_reducido': {
            'base': base_imponible,
            'iva': monto_iva_reducido,
            'total': total_reducido
        },
        'todos_los_ivas': todos_los_ivas
    }