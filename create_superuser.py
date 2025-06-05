import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sysfree.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.filter(email='admin@mail.com').first()

if user:
    print('El superusuario ya existe')
else:
    print('Creando superusuario...')
    User.objects.create_superuser(
        email='admin@mail.com',
        password='admin123',
        nombres='Administrador',
        apellidos='Sistema'
    )
    print('Superusuario creado correctamente')