import re
from django.utils.deprecation import MiddlewareMixin


class MobileDetectionMiddleware(MiddlewareMixin):
    """
    Middleware para detectar dispositivos móviles y establecer una variable en la request.
    """
    
    def process_request(self, request):
        """
        Detecta si la solicitud proviene de un dispositivo móvil.
        
        Args:
            request: Objeto request de Django
            
        Returns:
            None
        """
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        
        # Patrones para detectar dispositivos móviles
        mobile_patterns = [
            'mobile', 'android', 'iphone', 'ipod', 'ipad', 'windows phone',
            'blackberry', 'opera mini', 'opera mobi', 'webos'
        ]
        
        # Verificar si el user agent coincide con algún patrón móvil
        is_mobile = any(pattern in user_agent for pattern in mobile_patterns)
        
        # Establecer la variable en la request
        request.is_mobile = is_mobile
        
        # También verificar si es una tablet
        tablet_patterns = ['ipad', 'android(?!.*mobile)', 'tablet']
        is_tablet = any(re.search(pattern, user_agent) for pattern in tablet_patterns)
        
        request.is_tablet = is_tablet
        
        # Determinar el tipo de dispositivo
        if is_tablet:
            request.device_type = 'tablet'
        elif is_mobile:
            request.device_type = 'mobile'
        else:
            request.device_type = 'desktop'
        
        return None