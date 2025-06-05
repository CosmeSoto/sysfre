from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner or admin
        if hasattr(obj, 'usuario'):
            return obj.usuario == request.user or request.user.is_staff
        elif hasattr(obj, 'creado_por'):
            return obj.creado_por == request.user or request.user.is_staff
        elif hasattr(obj, 'cliente') and hasattr(request.user, 'cliente'):
            return obj.cliente == request.user.cliente or request.user.is_staff
        
        # If we can't determine ownership, only allow admins
        return request.user.is_staff


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit objects.
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to admin users.
        return request.user.is_staff