"""
ASGI config for sysfree project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sysfree.settings')

application = get_asgi_application()