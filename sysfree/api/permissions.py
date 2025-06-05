from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado para permitir solo a administradores editar objetos.
    Los usuarios no administradores solo pueden ver.
    """
    
    def has_permission(self, request, view):
        # Permitir métodos GET, HEAD, OPTIONS a cualquier usuario
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Permitir escritura solo a administradores
        return request.user and request.user.is_staff


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permiso personalizado para permitir a los propietarios de un objeto editarlo.
    Los administradores pueden editar cualquier objeto.
    """
    
    def has_object_permission(self, request, view, obj):
        # Permitir métodos GET, HEAD, OPTIONS a cualquier usuario autenticado
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Permitir escritura a administradores
        if request.user and request.user.is_staff:
            return True
        
        # Verificar si el objeto tiene un campo 'cliente' o 'usuario'
        if hasattr(obj, 'cliente'):
            return obj.cliente.usuario == request.user
        
        if hasattr(obj, 'usuario'):
            return obj.usuario == request.user
        
        if hasattr(obj, 'creado_por'):
            return obj.creado_por == request.user
        
        return False


class IsSuperUserOnly(permissions.BasePermission):
    """
    Permiso que solo permite acceso a superusuarios.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class HasModulePermission(permissions.BasePermission):
    """
    Permiso que verifica si el usuario tiene permisos para un módulo específico.
    """
    
    def __init__(self, module_name):
        self.module_name = module_name
        self.perm_name = f"access_{module_name}"
    
    def has_permission(self, request, view):
        if request.user and request.user.is_superuser:
            return True
        
        return request.user and request.user.has_perm(self.perm_name)


class HasAPIAccess(permissions.BasePermission):
    """
    Permiso que verifica si el usuario tiene acceso a la API.
    """
    
    def has_permission(self, request, view):
        if request.user and request.user.is_superuser:
            return True
        
        return request.user and request.user.has_perm('api.access_api')