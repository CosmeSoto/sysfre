from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import AsientoContable, LineaAsiento, Comprobante

# Las señales de auditoría están en core.signals


@receiver(pre_save, sender=AsientoContable)
def generar_numero_asiento(sender, instance, **kwargs):
    """
    Genera un número único para el asiento contable si no tiene uno.
    """
    if not instance.numero:
        year = timezone.now().year
        month = timezone.now().month
        
        # Obtener el último número de este año/mes
        ultimo = AsientoContable.objects.filter(
            numero__startswith=f'A{year}{month:02d}'
        ).order_by('-numero').first()
        
        if ultimo:
            # Extraer el número secuencial y aumentarlo en 1
            try:
                secuencial = int(ultimo.numero[-5:]) + 1
            except ValueError:
                secuencial = 1
        else:
            secuencial = 1
        
        # Formatear el número
        instance.numero = f'A{year}{month:02d}{secuencial:05d}'


@receiver(post_save, sender=LineaAsiento)
def verificar_balance_asiento(sender, instance, **kwargs):
    """
    Verifica si el asiento está balanceado después de guardar una línea.
    """
    asiento = instance.asiento
    
    # Si el asiento está en estado borrador y está balanceado, validarlo automáticamente
    if asiento.estado == 'borrador' and asiento.esta_balanceado:
        # Solo validar si tiene al menos dos líneas
        if asiento.lineas.count() >= 2:
            asiento.estado = 'validado'
            asiento.save(update_fields=['estado'])


@receiver(post_save, sender=Comprobante)
def crear_asiento_comprobante(sender, instance, created, **kwargs):
    """
    Crea un asiento contable cuando se emite un comprobante.
    """
    # Solo crear asiento si el comprobante está emitido y no tiene asiento
    if instance.estado == 'emitido' and not instance.asiento_contable:
        # Aquí se implementaría la lógica para crear el asiento contable
        # según el tipo de comprobante
        pass