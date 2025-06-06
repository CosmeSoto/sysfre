# Generated by Django 5.2 on 2025-05-29 20:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0001_initial'),
        ('inventario', '0001_initial'),
        ('reparaciones', '0002_initial'),
        ('ventas', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='detalleventa',
            options={'verbose_name': 'detalle de venta', 'verbose_name_plural': 'detalles de venta'},
        ),
        migrations.AlterField(
            model_name='pago',
            name='metodo',
            field=models.CharField(choices=[('efectivo', 'Efectivo'), ('tarjeta', 'Tarjeta de crédito/débito'), ('transferencia', 'Transferencia bancaria'), ('cheque', 'Cheque'), ('credito', 'Crédito'), ('otro', 'Otro')], max_length=15, verbose_name='método'),
        ),
        migrations.AlterField(
            model_name='pago',
            name='numero_cheque',
            field=models.CharField(blank=True, max_length=30, verbose_name='número de cheque'),
        ),
        migrations.AlterField(
            model_name='pago',
            name='numero_cuenta',
            field=models.CharField(blank=True, max_length=30, verbose_name='número de cuenta'),
        ),
        migrations.AlterField(
            model_name='pago',
            name='numero_tarjeta',
            field=models.CharField(blank=True, max_length=19, verbose_name='número de tarjeta'),
        ),
        migrations.AlterField(
            model_name='pago',
            name='titular_tarjeta',
            field=models.CharField(blank=True, max_length=100, verbose_name='titular de tarjeta'),
        ),
        migrations.AlterField(
            model_name='venta',
            name='direccion_envio',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='ventas_envio', to='clientes.direccioncliente', verbose_name='dirección de envío'),
        ),
        migrations.AlterField(
            model_name='venta',
            name='direccion_facturacion',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='ventas_facturacion', to='clientes.direccioncliente', verbose_name='dirección de facturación'),
        ),
        migrations.AlterField(
            model_name='venta',
            name='estado',
            field=models.CharField(choices=[('borrador', 'Borrador'), ('emitida', 'Emitida'), ('pagada', 'Pagada'), ('anulada', 'Anulada')], default='borrador', max_length=10, verbose_name='estado'),
        ),
        migrations.AlterField(
            model_name='venta',
            name='tipo',
            field=models.CharField(choices=[('factura', 'Factura'), ('nota_venta', 'Nota de Venta'), ('ticket', 'Ticket')], default='factura', max_length=10, verbose_name='tipo'),
        ),
        migrations.CreateModel(
            name='Proforma',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='fecha de creación')),
                ('fecha_modificacion', models.DateTimeField(auto_now=True, verbose_name='fecha de modificación')),
                ('activo', models.BooleanField(default=True, verbose_name='activo')),
                ('numero', models.CharField(max_length=20, unique=True, verbose_name='número')),
                ('fecha', models.DateTimeField(auto_now_add=True, verbose_name='fecha')),
                ('estado', models.CharField(choices=[('borrador', 'Borrador'), ('enviada', 'Enviada'), ('aceptada', 'Aceptada'), ('rechazada', 'Rechazada'), ('vencida', 'Vencida'), ('facturada', 'Facturada')], default='borrador', max_length=10, verbose_name='estado')),
                ('subtotal', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='subtotal')),
                ('iva', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='IVA')),
                ('descuento', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='descuento')),
                ('total', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='total')),
                ('validez', models.PositiveIntegerField(default=15, verbose_name='validez (días)')),
                ('notas', models.TextField(blank=True, verbose_name='notas')),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='proformas', to='clientes.cliente', verbose_name='cliente')),
                ('creado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_creados', to=settings.AUTH_USER_MODEL, verbose_name='creado por')),
                ('direccion_envio', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='proformas_envio', to='clientes.direccioncliente', verbose_name='dirección de envío')),
                ('direccion_facturacion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='proformas_facturacion', to='clientes.direccioncliente', verbose_name='dirección de facturación')),
                ('factura', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='proformas', to='ventas.venta', verbose_name='factura')),
                ('modificado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_modificados', to=settings.AUTH_USER_MODEL, verbose_name='modificado por')),
                ('reparacion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='proformas', to='reparaciones.reparacion', verbose_name='reparación')),
            ],
            options={
                'verbose_name': 'proforma',
                'verbose_name_plural': 'proformas',
                'ordering': ['-fecha'],
            },
        ),
        migrations.CreateModel(
            name='DetalleProforma',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='fecha de creación')),
                ('fecha_modificacion', models.DateTimeField(auto_now=True, verbose_name='fecha de modificación')),
                ('activo', models.BooleanField(default=True, verbose_name='activo')),
                ('cantidad', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='cantidad')),
                ('precio_unitario', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='precio unitario')),
                ('descuento', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='descuento')),
                ('iva', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='IVA')),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='subtotal')),
                ('total', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='total')),
                ('creado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_creados', to=settings.AUTH_USER_MODEL, verbose_name='creado por')),
                ('modificado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_modificados', to=settings.AUTH_USER_MODEL, verbose_name='modificado por')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='detalles_proforma', to='inventario.producto', verbose_name='producto')),
                ('proforma', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detalles', to='ventas.proforma', verbose_name='proforma')),
            ],
            options={
                'verbose_name': 'detalle de proforma',
                'verbose_name_plural': 'detalles de proforma',
            },
        ),
    ]
