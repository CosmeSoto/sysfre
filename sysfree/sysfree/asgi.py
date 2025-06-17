"""
Configuración ASGI para el proyecto sysfree.

Define la aplicación ASGI para servidores como Uvicorn o Daphne, compatible
con aplicaciones síncronas y asíncronas (por ejemplo, WebSockets con Django Channels).
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sysfree.settings')

application = get_asgi_application()