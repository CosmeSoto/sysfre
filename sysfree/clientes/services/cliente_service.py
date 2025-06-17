from django.db.models import Q
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache
from ..models import Cliente, ContactoCliente, DireccionCliente
from core.models import Usuario


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
        # Crear una clave única para el caché
        cache_key = f'cliente_service_buscar_{termino}'
        
        # Intentar obtener del caché
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Si no está en caché, realizar la consulta
        clientes = Cliente.objects.filter(
            Q(identificacion__icontains=termino) |
            Q(nombres__icontains=termino) |
            Q(apellidos__icontains=termino) |
            Q(nombre_comercial__icontains=termino) |
            Q(email__icontains=termino) |
            Q(telefono__icontains=termino) |
            Q(celular__icontains=termino)
        ).filter(activo=True)
        
        # Guardar en caché por 5 minutos
        cache.set(cache_key, clientes, 60 * 5)
        
        return clientes
    
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
        # Crear el cliente
        cliente = Cliente.objects.create(**datos_cliente)
        
        usuario = None
        password = None
        
        # Crear usuario si se solicita y hay email
        if crear_usuario and cliente.email:
            # Verificar si ya existe un usuario con ese email
            try:
                usuario = Usuario.objects.get(email=cliente.email)
            except Usuario.DoesNotExist:
                # Generar una contraseña aleatoria
                password = get_random_string(12)
                
                # Crear el usuario
                usuario = Usuario.objects.create_user(
                    email=cliente.email,
                    password=password,
                    nombres=cliente.nombres,
                    apellidos=cliente.apellidos,
                    is_active=True
                )
            
            # Asignar el usuario al cliente
            cliente.usuario = usuario
            cliente.save(update_fields=['usuario'])
            
            # Enviar email con las credenciales
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
        # Crear una clave única para el caché
        cache_key = f'cliente_direccion_facturacion_{cliente.id}'
        
        # Intentar obtener del caché
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        try:
            direccion = DireccionCliente.objects.get(
                cliente=cliente,
                tipo='facturacion',
                es_principal=True,
                activo=True
            )
        except DireccionCliente.DoesNotExist:
            # Si no hay dirección principal, intentar obtener cualquier dirección de facturación
            try:
                direccion = DireccionCliente.objects.filter(
                    cliente=cliente,
                    tipo='facturacion',
                    activo=True
                ).first()
            except DireccionCliente.DoesNotExist:
                direccion = None
        
        # Guardar en caché por 30 minutos
        cache.set(cache_key, direccion, 60 * 30)
        
        return direccion
    
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