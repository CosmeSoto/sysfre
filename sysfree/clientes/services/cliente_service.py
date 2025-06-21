from django.db.models import Q
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from ..models import Cliente, ContactoCliente, DireccionCliente
from core.models import Usuario
from core.services.cache_service import CacheService
from core.services.auditoria_service import AuditoriaService


class ClienteService:
    """Servicio para gestionar operaciones con clientes."""
    
    @classmethod
    def buscar_clientes(cls, termino):
        """
        Busca clientes por varios criterios.
        
        Args:
            termino (str): Término de búsqueda
            
        Returns:
            QuerySet: Clientes que coinciden con la búsqueda
        """
        cache_key = f'cliente_buscar_{termino}'
        
        def buscar_query():
            return list(Cliente.objects.filter(
                Q(identificacion__icontains=termino) |
                Q(nombres__icontains=termino) |
                Q(apellidos__icontains=termino) |
                Q(nombre_comercial__icontains=termino) |
                Q(email__icontains=termino) |
                Q(telefono__icontains=termino) |
                Q(celular__icontains=termino)
            ).filter(activo=True))
        
        return CacheService.get_or_set(cache_key, buscar_query, 300)  # 5 minutos
    
    @classmethod
    def crear_cliente_con_usuario(cls, datos_cliente, crear_usuario=False, enviar_email=False):
        """
        Crea un cliente y opcionalmente un usuario asociado.
        
        Args:
            datos_cliente (dict): Datos del cliente
            crear_usuario (bool): Indica si se debe crear un usuario
            enviar_email (bool): Indica si se debe enviar un email con las credenciales
            
        Returns:
            tuple: (Cliente creado, Usuario creado, Contraseña generada)
        """
        cliente = Cliente.objects.create(**datos_cliente)
        
        # Registrar auditoría
        AuditoriaService.registrar_actividad_personalizada(
            accion="CLIENTE_CREADO",
            descripcion=f"Cliente creado: {cliente.nombre_completo} ({cliente.identificacion})",
            modelo="Cliente",
            objeto_id=cliente.id,
            datos={'identificacion': cliente.identificacion, 'tipo': cliente.tipo_cliente}
        )
        
        usuario = None
        password = None
        
        if crear_usuario and cliente.email:
            try:
                usuario = Usuario.objects.get(email=cliente.email)
            except Usuario.DoesNotExist:
                password = get_random_string(12)
                usuario = Usuario.objects.create_user(
                    email=cliente.email,
                    password=password,
                    nombres=cliente.nombres,
                    apellidos=cliente.apellidos,
                    is_active=True
                )
            
            cliente.usuario = usuario
            cliente.save(update_fields=['usuario'])
            
            if enviar_email and password:
                cls.send_welcome_email(cliente, password)
        
        return cliente, usuario, password
    
    @classmethod
    def agregar_contacto(cls, cliente, datos_contacto):
        """
        Agrega un contacto a un cliente.
        
        Args:
            cliente (Cliente): Cliente al que se agrega el contacto
            datos_contacto (dict): Datos del contacto
            
        Returns:
            ContactoCliente: Contacto creado
        """
        return ContactoCliente.objects.create(cliente=cliente, **datos_contacto)
    
    @classmethod
    def agregar_direccion(cls, cliente, datos_direccion):
        """
        Agrega una dirección a un cliente.
        
        Args:
            cliente (Cliente): Cliente al que se agrega la dirección
            datos_direccion (dict): Datos de la dirección
            
        Returns:
            DireccionCliente: Dirección creada
        """
        return DireccionCliente.objects.create(cliente=cliente, **datos_direccion)
    
    @classmethod
    def obtener_direccion_facturacion(cls, cliente):
        """
        Obtiene la dirección de facturación principal del cliente.
        
        Args:
            cliente (Cliente): Cliente a consultar
            
        Returns:
            DireccionCliente: Dirección de facturación principal o None
        """
        cache_key = f'cliente_dir_fact_{cliente.id}'
        
        def obtener_direccion():
            try:
                return DireccionCliente.objects.get(
                    cliente=cliente,
                    tipo='facturacion',
                    es_principal=True,
                    activo=True
                )
            except DireccionCliente.DoesNotExist:
                return DireccionCliente.objects.filter(
                    cliente=cliente,
                    tipo='facturacion',
                    activo=True
                ).first()
        
        return CacheService.get_or_set(cache_key, obtener_direccion, 1800)  # 30 minutos
    
    @classmethod
    def send_welcome_email(cls, cliente, password):
        """
        Envía un correo de bienvenida al cliente con credenciales de acceso al portal.
        
        Args:
            cliente (Cliente): Instancia del modelo Cliente
            password (str): Contraseña generada para el usuario
            
        Raises:
            ValueError: Si el cliente no tiene email válido o acceso al portal
            Exception: Si falla el envío del correo
        """
        if not cliente.email or not cliente.tiene_acceso_portal:
            raise ValueError("El cliente no tiene email válido o acceso al portal.")
        
        subject = "Bienvenido al Portal de Clientes de Freecom"
        message = (
            f"Estimado/a {cliente.nombre_completo},\n\n"
            "Le damos la bienvenida al portal de clientes de Freecom. "
            "A continuación, encontrará sus credenciales de acceso:\n\n"
            f"Email: {cliente.email}\n"
            f"Contraseña: {password}\n\n"
            "Por seguridad, le recomendamos cambiar su contraseña al iniciar sesión.\n"
            "Acceda al portal en: https://freecom.com/portal\n\n"
            "Gracias por confiar en nosotros,\n"
            "Equipo Freecom"
        )
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [cliente.email]

        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False,
        )