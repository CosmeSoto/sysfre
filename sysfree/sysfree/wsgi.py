"""
Configuración WSGI para el proyecto sysfree.

Define la aplicación WSGI para servidores como Gunicorn en entornos de producción.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sysfree.settings')

application = get_wsgi_application()