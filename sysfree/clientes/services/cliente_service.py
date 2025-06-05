from django.db.models import Q
from django.utils.crypto import get_random_string
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
        return Cliente.objects.filter(
            Q(identificacion__icontains=termino) |
            Q(nombres__icontains=termino) |
            Q(apellidos__icontains=termino) |
            Q(nombre_comercial__icontains=termino) |
            Q(email__icontains=termino) |
            Q(telefono__icontains=termino) |
            Q(celular__icontains=termino)
        ).filter(activo=True)
    
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
                # send_welcome_email(cliente, password)
                pass
        
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
        try:
            return DireccionCliente.objects.get(
                cliente=cliente,
                tipo='facturacion',
                es_principal=True,
                activo=True
            )
        except DireccionCliente.DoesNotExist:
            # Si no hay dirección principal, intentar obtener cualquier dirección de facturación
            try:
                return DireccionCliente.objects.filter(
                    cliente=cliente,
                    tipo='facturacion',
                    activo=True
                ).first()
            except DireccionCliente.DoesNotExist:
                return None