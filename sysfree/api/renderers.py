from rest_framework.renderers import JSONRenderer
import json


class PrettyJSONRenderer(JSONRenderer):
    """
    Renderizador JSON con formato legible para humanos.
    """
    
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if renderer_context and renderer_context.get('indent'):
            indent = renderer_context.get('indent')
        else:
            indent = 4
            
        response = super().render(data, accepted_media_type, renderer_context)
        
        # Si es una respuesta binaria, devolverla tal cual
        if isinstance(response, bytes):
            try:
                parsed_data = json.loads(response.decode('utf-8'))
                return json.dumps(parsed_data, indent=indent).encode('utf-8')
            except (ValueError, UnicodeDecodeError):
                return response
                
        return response


class APIResponseRenderer(JSONRenderer):
    """
    Renderizador que envuelve todas las respuestas en un formato estándar.
    """
    
    def render(self, data, accepted_media_type=None, renderer_context=None):
        # Obtener el código de estado de la respuesta
        status_code = renderer_context.get('response').status_code
        
        # Si ya es una respuesta de error con el formato correcto, no modificarla
        if isinstance(data, dict) and 'error' in data:
            response_dict = data
        else:
            # Crear el diccionario de respuesta estándar
            response_dict = {
                'error': status_code >= 400,
                'status_code': status_code,
                'data': data
            }
            
            # Añadir mensaje según el código de estado
            if status_code >= 400:
                response_dict['message'] = renderer_context.get('response').status_text
            
        # Renderizar la respuesta
        return super().render(response_dict, accepted_media_type, renderer_context)