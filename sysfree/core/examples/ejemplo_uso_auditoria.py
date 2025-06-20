"""
Ejemplos de cómo usar el sistema de auditoría mejorado en diferentes partes del sistema.
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, DeleteView
from ..services.auditoria_service import AuditoriaService
from ..mixins.auditoria_mixins import AuditoriaMixin
from ..constants import AccionesAuditoria, NivelesLog


# Ejemplo 1: Vista de creación de venta con auditoría
class VentaCreateView(AuditoriaMixin, CreateView):
    """Ejemplo de vista para crear ventas con auditoría automática."""
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Registrar la creación de la venta
        AuditoriaService.venta_creada(
            venta=self.object,
            detalles=form.cleaned_data.get('detalles', [])
        )
        
        messages.success(self.request, 'Venta creada exitosamente')
        return response


# Ejemplo 2: Función de vista para anular venta
def anular_venta(request, venta_id):
    """Ejemplo de función para anular una venta con auditoría."""
    try:
        venta = Venta.objects.get(id=venta_id)
        motivo = request.POST.get('motivo', 'Sin motivo especificado')
        
        # Cambiar estado de la venta
        venta.estado = 'ANULADA'
        venta.save()
        
        # Registrar la anulación
        AuditoriaService.venta_anulada(venta, motivo)
        
        messages.success(request, 'Venta anulada correctamente')
        
    except Venta.DoesNotExist:
        messages.error(request, 'Venta no encontrada')
        
    return redirect('ventas:lista')


# Ejemplo 3: Servicio de inventario con auditoría
class InventarioService:
    """Ejemplo de servicio que maneja inventario con auditoría."""
    
    @staticmethod
    def actualizar_stock(producto, nueva_cantidad, motivo="Ajuste manual"):
        """Actualiza el stock de un producto y registra la auditoría."""
        cantidad_anterior = producto.stock
        producto.stock = nueva_cantidad
        producto.save()
        
        # Registrar el cambio de stock
        AuditoriaService.stock_actualizado(
            producto=producto,
            cantidad_anterior=cantidad_anterior,
            cantidad_nueva=nueva_cantidad,
            motivo=motivo
        )
        
        return producto


# Ejemplo 4: Decorador para auditar funciones específicas
def auditar_accion(accion, descripcion_template=None):
    """Decorador para auditar automáticamente funciones."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                resultado = func(*args, **kwargs)
                
                # Generar descripción
                if descripcion_template:
                    descripcion = descripcion_template.format(**kwargs)
                else:
                    descripcion = f"Ejecutada función {func.__name__}"
                
                # Registrar actividad exitosa
                AuditoriaService.registrar_actividad_personalizada(
                    accion=accion,
                    descripcion=descripcion,
                    nivel=NivelesLog.INFO
                )
                
                return resultado
                
            except Exception as e:
                # Registrar error
                AuditoriaService.registrar_actividad_personalizada(
                    accion=f"{accion}_ERROR",
                    descripcion=f"Error en {func.__name__}: {str(e)}",
                    nivel=NivelesLog.ERROR
                )
                raise
        
        return wrapper
    return decorator


# Ejemplo 5: Uso del decorador
@auditar_accion(
    accion="BACKUP_SISTEMA",
    descripcion_template="Backup del sistema creado en {ruta}"
)
def crear_backup(ruta="/backups/"):
    """Ejemplo de función que crea backup del sistema."""
    import datetime
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo_backup = f"{ruta}backup_{timestamp}.sql"
    
    return archivo_backup