# Generated by Django 5.2 on 2025-06-20 02:39

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='correo electrónico')),
                ('nombres', models.CharField(blank=True, max_length=150, verbose_name='nombres')),
                ('apellidos', models.CharField(blank=True, max_length=150, verbose_name='apellidos')),
                ('telefono', models.CharField(blank=True, max_length=15, verbose_name='teléfono')),
                ('foto', models.ImageField(blank=True, null=True, upload_to='usuarios/fotos/', verbose_name='foto de perfil')),
                ('fecha_nacimiento', models.DateField(blank=True, null=True, verbose_name='fecha de nacimiento')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='fecha de creación')),
                ('fecha_modificacion', models.DateTimeField(auto_now=True, verbose_name='fecha de modificación')),
                ('ultimo_login', models.DateTimeField(blank=True, null=True, verbose_name='último acceso')),
                ('is_active', models.BooleanField(default=True, verbose_name='activo')),
                ('is_staff', models.BooleanField(default=False, verbose_name='staff')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'usuario',
                'verbose_name_plural': 'usuarios',
                'ordering': ['email'],
            },
        ),
        migrations.CreateModel(
            name='Empresa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='fecha de creación')),
                ('fecha_modificacion', models.DateTimeField(auto_now=True, verbose_name='fecha de modificación')),
                ('activo', models.BooleanField(default=True, verbose_name='activo')),
                ('nombre', models.CharField(max_length=200, verbose_name='nombre')),
                ('nombre_comercial', models.CharField(blank=True, max_length=200, verbose_name='nombre comercial')),
                ('ruc', models.CharField(max_length=13, unique=True, verbose_name='RUC')),
                ('direccion', models.TextField(verbose_name='dirección')),
                ('telefono', models.CharField(blank=True, max_length=15, verbose_name='teléfono')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='correo electrónico')),
                ('sitio_web', models.URLField(blank=True, verbose_name='sitio web')),
                ('logo', models.ImageField(blank=True, null=True, upload_to='empresa/logos/', verbose_name='logo')),
                ('regimen_fiscal', models.CharField(blank=True, max_length=100, verbose_name='régimen fiscal')),
                ('representante_legal', models.CharField(blank=True, max_length=200, verbose_name='representante legal')),
                ('cedula_representante', models.CharField(blank=True, max_length=10, verbose_name='cédula del representante')),
                ('descripcion', models.TextField(blank=True, verbose_name='descripción')),
                ('horario', models.TextField(blank=True, verbose_name='horario de atención')),
                ('facebook', models.URLField(blank=True, verbose_name='Facebook')),
                ('instagram', models.URLField(blank=True, verbose_name='Instagram')),
                ('twitter', models.URLField(blank=True, verbose_name='Twitter')),
                ('ambiente_facturacion', models.CharField(choices=[('1', 'Pruebas'), ('2', 'Producción')], default='1', max_length=1, verbose_name='ambiente de facturación')),
                ('ruta_certificado', models.CharField(blank=True, help_text='Ruta absoluta al archivo .p12 en el servidor.', max_length=255, verbose_name='ruta del certificado P12')),
                ('clave_certificado', models.CharField(blank=True, max_length=255, verbose_name='clave del certificado')),
                ('url_recepcion_pruebas', models.URLField(blank=True, default='https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl', verbose_name='URL Recepción (Pruebas)')),
                ('url_autorizacion_pruebas', models.URLField(blank=True, default='https://celcer.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl', verbose_name='URL Autorización (Pruebas)')),
                ('url_recepcion_produccion', models.URLField(blank=True, default='https://cel.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl', verbose_name='URL Recepción (Producción)')),
                ('url_autorizacion_produccion', models.URLField(blank=True, default='https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl', verbose_name='URL Autorización (Producción)')),
                ('creado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_creados', to=settings.AUTH_USER_MODEL, verbose_name='creado por')),
                ('modificado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_modificados', to=settings.AUTH_USER_MODEL, verbose_name='modificado por')),
            ],
            options={
                'verbose_name': 'empresa',
                'verbose_name_plural': 'empresas',
            },
        ),
        migrations.CreateModel(
            name='LogActividad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateTimeField(auto_now_add=True, verbose_name='fecha')),
                ('ip', models.GenericIPAddressField(blank=True, null=True, verbose_name='dirección IP')),
                ('nivel', models.CharField(choices=[('info', 'Información'), ('warning', 'Advertencia'), ('error', 'Error'), ('critical', 'Crítico')], default='info', max_length=10, verbose_name='nivel')),
                ('tipo', models.CharField(choices=[('sistema', 'Sistema'), ('usuario', 'Usuario'), ('seguridad', 'Seguridad'), ('negocio', 'Negocio')], default='sistema', max_length=10, verbose_name='tipo')),
                ('accion', models.CharField(max_length=100, verbose_name='acción')),
                ('descripcion', models.TextField(verbose_name='descripción')),
                ('modelo', models.CharField(blank=True, max_length=100, verbose_name='modelo')),
                ('objeto_id', models.CharField(blank=True, max_length=50, verbose_name='ID del objeto')),
                ('datos', models.JSONField(blank=True, null=True, verbose_name='datos adicionales')),
                ('datos_anteriores', models.JSONField(blank=True, help_text='Estado del objeto antes de la modificación, si aplica.', null=True, verbose_name='datos anteriores')),
                ('user_agent', models.CharField(blank=True, help_text='Información del cliente/navegador del usuario.', max_length=255, null=True, verbose_name='user agent')),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='usuario')),
            ],
            options={
                'verbose_name': 'log de actividad',
                'verbose_name_plural': 'logs de actividad',
                'ordering': ['-fecha'],
            },
        ),
        migrations.CreateModel(
            name='TipoIVA',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='fecha de creación')),
                ('fecha_modificacion', models.DateTimeField(auto_now=True, verbose_name='fecha de modificación')),
                ('activo', models.BooleanField(default=True, verbose_name='activo')),
                ('nombre', models.CharField(max_length=50, unique=True, verbose_name='nombre')),
                ('codigo', models.CharField(max_length=20, unique=True, verbose_name='código')),
                ('porcentaje', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='porcentaje')),
                ('descripcion', models.TextField(blank=True, verbose_name='descripción')),
                ('es_default', models.BooleanField(default=False, verbose_name='es predeterminado')),
                ('creado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_creados', to=settings.AUTH_USER_MODEL, verbose_name='creado por')),
                ('modificado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_modificados', to=settings.AUTH_USER_MODEL, verbose_name='modificado por')),
            ],
            options={
                'verbose_name': 'tipo de IVA',
                'verbose_name_plural': 'tipos de IVA',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='ConfiguracionSistema',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='fecha de creación')),
                ('fecha_modificacion', models.DateTimeField(auto_now=True, verbose_name='fecha de modificación')),
                ('activo', models.BooleanField(default=True, verbose_name='activo')),
                ('PREFIJO_FACTURA', models.CharField(default='FAC-', max_length=10, verbose_name='prefijo factura')),
                ('PREFIJO_PROFORMA', models.CharField(default='PRO-', max_length=10, verbose_name='prefijo proforma')),
                ('PREFIJO_NOTA_VENTA', models.CharField(default='NV-', max_length=10, verbose_name='prefijo nota de venta')),
                ('PREFIJO_TICKET', models.CharField(default='TIK-', max_length=10, verbose_name='prefijo ticket')),
                ('INICIO_FACTURA', models.PositiveIntegerField(default=1, verbose_name='inicio numeración factura')),
                ('INICIO_PROFORMA', models.PositiveIntegerField(default=1, verbose_name='inicio numeración proforma')),
                ('INICIO_NOTA_VENTA', models.PositiveIntegerField(default=1, verbose_name='inicio numeración nota de venta')),
                ('INICIO_TICKET', models.PositiveIntegerField(default=1, verbose_name='inicio numeración ticket')),
                ('creado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_creados', to=settings.AUTH_USER_MODEL, verbose_name='creado por')),
                ('modificado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_modificados', to=settings.AUTH_USER_MODEL, verbose_name='modificado por')),
                ('tipo_iva_default', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='configuraciones', to='core.tipoiva', verbose_name='tipo de IVA predeterminado')),
            ],
            options={
                'verbose_name': 'configuración del sistema',
                'verbose_name_plural': 'configuraciones del sistema',
            },
        ),
        migrations.CreateModel(
            name='Sucursal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='fecha de creación')),
                ('fecha_modificacion', models.DateTimeField(auto_now=True, verbose_name='fecha de modificación')),
                ('activo', models.BooleanField(default=True, verbose_name='activo')),
                ('nombre', models.CharField(max_length=200, verbose_name='nombre')),
                ('codigo', models.CharField(max_length=10, verbose_name='código')),
                ('direccion', models.TextField(verbose_name='dirección')),
                ('telefono', models.CharField(blank=True, max_length=15, verbose_name='teléfono')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='correo electrónico')),
                ('es_matriz', models.BooleanField(default=False, verbose_name='es matriz')),
                ('horario', models.TextField(blank=True, verbose_name='horario de atención')),
                ('creado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_creados', to=settings.AUTH_USER_MODEL, verbose_name='creado por')),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sucursales', to='core.empresa', verbose_name='empresa')),
                ('modificado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_modificados', to=settings.AUTH_USER_MODEL, verbose_name='modificado por')),
            ],
            options={
                'verbose_name': 'sucursal',
                'verbose_name_plural': 'sucursales',
                'unique_together': {('empresa', 'codigo')},
            },
        ),
    ]
