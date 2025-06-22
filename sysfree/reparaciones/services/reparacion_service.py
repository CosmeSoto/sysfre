from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from ..models import Reparacion, SeguimientoReparacion, RepuestoReparacion
from inventario.models import Producto
from core.services.auditoria_service import AuditoriaService


class ReparacionService:
    """Servicio para gestionar operaciones de reparaciones."""
    
    @classmethod
    @transaction.atomic
    def crear_reparacion(cls, cliente, tipo_equipo, marca, modelo, problema_reportado, 
                        numero_serie='', accesorios='', prioridad='media', tecnico=None, 
                        fecha_estimada_entrega=None, usuario=None):
        """
        Crea una nueva reparación.
        
        Args:
            cliente: Cliente de la reparación
            tipo_equipo: Tipo de equipo a reparar
            marca: Marca del equipo
            modelo: Modelo del equipo
            problema_reportado: Problema reportado por el cliente
            numero_serie: Número de serie del equipo
            accesorios: Accesorios entregados con el equipo
            prioridad: Prioridad de la reparación
            tecnico: Técnico asignado
            fecha_estimada_entrega: Fecha estimada de entrega
            usuario: Usuario que crea la reparación
            
        Returns:
            Reparacion: Reparación creada
        """
        # Generar número de reparación
        numero = cls._generar_numero_reparacion()
        
        # Crear la reparación
        reparacion = Reparacion(
            numero=numero,
            cliente=cliente,
            tipo_equipo=tipo_equipo,
            marca=marca,
            modelo=modelo,
            numero_serie=numero_serie,
            accesorios=accesorios,
            problema_reportado=problema_reportado,
            prioridad=prioridad,
            tecnico=tecnico,
            fecha_estimada_entrega=fecha_estimada_entrega
        )
        
        if usuario:
            reparacion.creado_por = usuario
            reparacion.modificado_por = usuario
        
        reparacion.save()
        
        # Registrar auditoría
        AuditoriaService.registrar_actividad_personalizada(
            accion="REPARACION_CREADA",
            descripcion=f"Reparación creada: {numero} - {tipo_equipo} {marca} {modelo}",
            modelo="Reparacion",
            objeto_id=reparacion.id,
            datos={'numero': numero, 'cliente': str(cliente), 'tipo_equipo': tipo_equipo}
        )
        
        return reparacion
    
    @classmethod
    def cambiar_estado(cls, reparacion, nuevo_estado, comentario='', notificar_cliente=False, usuario=None):
        """
        Cambia el estado de una reparación y registra el seguimiento.
        
        Args:
            reparacion: Reparación a modificar
            nuevo_estado: Nuevo estado de la reparación
            comentario: Comentario sobre el cambio de estado
            notificar_cliente: Indica si se debe notificar al cliente
            usuario: Usuario que realiza el cambio
            
        Returns:
            tuple: (Reparacion, SeguimientoReparacion)
        """
        estado_anterior = reparacion.estado
        reparacion.estado = nuevo_estado
        
        # Si el estado es 'entregado', registrar la fecha de entrega
        if nuevo_estado == 'entregado' and not reparacion.fecha_entrega:
            reparacion.fecha_entrega = timezone.now()
        
        if usuario:
            reparacion.modificado_por = usuario
        
        reparacion.save()
        
        # Crear seguimiento
        seguimiento = SeguimientoReparacion(
            reparacion=reparacion,
            estado_anterior=estado_anterior,
            estado_nuevo=nuevo_estado,
            comentario=comentario or f'Estado cambiado de {estado_anterior} a {nuevo_estado}',
            notificado_cliente=notificar_cliente
        )
        
        if notificar_cliente:
            seguimiento.fecha_notificacion = timezone.now()
        
        if usuario:
            seguimiento.creado_por = usuario
            seguimiento.modificado_por = usuario
        
        seguimiento.save()
        
        # Registrar auditoría
        AuditoriaService.registrar_actividad_personalizada(
            accion="CAMBIO_ESTADO_REPARACION",
            descripcion=f"Reparación {reparacion.numero} cambió de {estado_anterior} a {nuevo_estado}",
            modelo="Reparacion",
            objeto_id=reparacion.id,
            datos={'estado_anterior': estado_anterior, 'estado_nuevo': nuevo_estado}
        )
        
        # Notificar al cliente si se solicita
        if notificar_cliente:
            cls._notificar_cliente(reparacion, seguimiento)
        
        return reparacion, seguimiento
    
    @classmethod
    @transaction.atomic
    def agregar_repuesto(cls, reparacion, producto, cantidad, precio_unitario=None, usuario=None):
        """
        Agrega un repuesto a una reparación.
        
        Args:
            reparacion: Reparación a la que se agrega el repuesto
            producto: Producto a agregar como repuesto
            cantidad: Cantidad del producto
            precio_unitario: Precio unitario del producto (si es None, se usa el precio de venta)
            usuario: Usuario que agrega el repuesto
            
        Returns:
            RepuestoReparacion: Repuesto agregado
        """
        if precio_unitario is None:
            precio_unitario = producto.precio_venta
        
        repuesto = RepuestoReparacion(
            reparacion=reparacion,
            producto=producto,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            subtotal=cantidad * precio_unitario
        )
        
        if usuario:
            repuesto.creado_por = usuario
            repuesto.modificado_por = usuario
        
        repuesto.save()
        
        # Registrar auditoría
        AuditoriaService.registrar_actividad_personalizada(
            accion="REPUESTO_AGREGADO",
            descripcion=f"Repuesto agregado a reparación {reparacion.numero}: {producto.nombre} x{cantidad}",
            modelo="RepuestoReparacion",
            objeto_id=repuesto.id,
            datos={'reparacion': reparacion.numero, 'producto': producto.nombre, 'cantidad': cantidad}
        )
        
        return repuesto
    
    @classmethod
    def buscar_reparaciones(cls, termino=None, estado=None, cliente=None, fecha_inicio=None, fecha_fin=None):
        """
        Busca reparaciones según varios criterios.
        
        Args:
            termino: Término de búsqueda general
            estado: Estado de la reparación
            cliente: Cliente de la reparación
            fecha_inicio: Fecha de inicio del rango
            fecha_fin: Fecha de fin del rango
            
        Returns:
            QuerySet: Reparaciones que coinciden con la búsqueda
        """
        query = Q(activo=True)
        
        if termino:
            query &= (
                Q(numero__icontains=termino) |
                Q(cliente__nombres__icontains=termino) |
                Q(cliente__apellidos__icontains=termino) |
                Q(cliente__nombre_comercial__icontains=termino) |
                Q(cliente__identificacion__icontains=termino) |
                Q(tipo_equipo__icontains=termino) |
                Q(marca__icontains=termino) |
                Q(modelo__icontains=termino) |
                Q(numero_serie__icontains=termino)
            )
        
        if estado:
            query &= Q(estado=estado)
        
        if cliente:
            query &= Q(cliente=cliente)
        
        if fecha_inicio:
            query &= Q(fecha_recepcion__gte=fecha_inicio)
        
        if fecha_fin:
            query &= Q(fecha_recepcion__lte=fecha_fin)
        
        return Reparacion.objects.filter(query).order_by('-fecha_recepcion')
    
    @classmethod
    def _generar_numero_reparacion(cls):
        """
        Genera un número único para la reparación.
        
        Returns:
            str: Número de reparación
        """
        year = timezone.now().year
        month = timezone.now().month
        
        # Obtener el último número de este año/mes
        ultimo = Reparacion.objects.filter(
            numero__startswith=f'R{year}{month:02d}'
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
        return f'R{year}{month:02d}{secuencial:05d}'
    
    @classmethod
    def _notificar_cliente(cls, reparacion, seguimiento):
        """
        Notifica al cliente sobre un cambio en la reparación.
        
        Args:
            reparacion: Reparación que cambió
            seguimiento: Seguimiento registrado
        """
        # Implementar la lógica de notificación (email, SMS, etc.)
        pass