# SysFree - Sistema de Gestión Empresarial

SysFree es un sistema completo de gestión empresarial que incluye módulos de inventario, ventas, clientes, reparaciones, contabilidad y tienda online con monitoreo avanzado.

## Características

- **Inventario**: Gestión de productos, categorías y proveedores
- **Ventas**: Creación de ventas, facturación y seguimiento de pagos
- **Clientes**: Gestión de clientes y sus datos de contacto
- **Reparaciones**: Seguimiento de órdenes de reparación y diagnósticos
- **Contabilidad**: Asientos contables y plan de cuentas
- **Reportes**: Generación de informes personalizados
- **Tienda Online**: Catálogo de productos y carrito de compras
- **Monitoreo**: Métricas de Prometheus, tareas asíncronas con Celery
- **Facturación Electrónica (Ecuador)**: Generación, firma y envío de comprobantes electrónicos al SRI.

## Requisitos del Sistema

- **Python**: 3.8+
- **Node.js**: 14+
- **PostgreSQL**: 12+
- **Redis**: 6+ (para Celery y cache)
- **Sistema Operativo**: Linux/macOS/Windows

## Instalación Completa

### 1. Configuración del Entorno

```bash
# Clonar el repositorio
git clone <repository-url>
cd freecom

# Crear entorno virtual
python -m venv env
source env/bin/activate  # Linux/macOS
# env\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configuración de Base de Datos

```bash
# Crear base de datos PostgreSQL
createdb sysfree_db

# Configurar variables de entorno (.env)
cp sysfree/.env.example sysfree/.env
# Editar .env con tus credenciales
```

### 3. Migración y Configuración Inicial

```bash
cd sysfree
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
```

### 4. Frontend (Opcional)

```bash
cd frontend
npm install
npm run build
```

## Servicios del Sistema

### Iniciar Todos los Servicios

```bash
# 1. Servidor Django
cd sysfree
source ../env/bin/activate
python manage.py runserver

# 2. Celery Worker (nueva terminal)
cd sysfree
source ../env/bin/activate
celery -A sysfree worker --loglevel=info --detach

# 3. Celery Beat Scheduler (nueva terminal)
cd sysfree
source ../env/bin/activate
celery -A sysfree beat --loglevel=info --detach
```

### Verificar Estado de Servicios

```bash
# Verificar procesos activos
ps aux | grep -E "(runserver|celery)" | grep -v grep

# Verificar métricas de Prometheus
curl http://localhost:8000/metrics/ | head -10

# Verificar logs
tail -f sysfree/logs/sysfree.log
```

### Detener Servicios

```bash
# Detener Celery
pkill -f "celery.*sysfree"

# Detener Django
pkill -f "python manage.py runserver"
```

## Monitoreo y Métricas

### Endpoint de Métricas
- **URL**: `http://localhost:8000/metrics/`
- **Autenticación**: Requiere login de Django
- **Formato**: Prometheus metrics

### Métricas Disponibles
- `cpu_usage_percent`: Uso de CPU del sistema
- `memory_usage_bytes`: Uso de memoria en bytes
- `celery_task_total`: Total de tareas de Celery procesadas
- `celery_task_duration_seconds`: Duración de tareas de Celery
- `http_requests_total`: Total de solicitudes HTTP
- `db_query_total`: Total de consultas a la base de datos

### Configuración de Prometheus

```yaml
# monitoring/prometheus/prometheus.yml
scrape_configs:
  - job_name: 'django'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics/'
```

## Tareas Programadas

### Tareas Automáticas (Celery Beat)
- **Métricas del Sistema**: Cada 60 segundos
- **Configuración**: `sysfree/settings.py` → `CELERY_BEAT_SCHEDULE`

### Ejecutar Tareas Manualmente

```bash
cd sysfree
source ../env/bin/activate

# Actualizar métricas del sistema
python -c "from core.tasks import update_system_metrics_task; update_system_metrics_task.delay()"
```

## Configuración de Producción

### Variables de Entorno Importantes

```bash
# .env
DEBUG=False
SECRET_KEY=tu-clave-secreta-segura
DB_NAME=sysfree_prod
DB_USER=sysfree_user
DB_PASSWORD=password-seguro
CACHE_LOCATION=redis://localhost:6379/1
PROMETHEUS_ALLOWED_IPS=127.0.0.1,::1,tu-ip-monitoreo
```

### Servicios en Producción

```bash
# Usar supervisor o systemd para gestionar servicios
# Ejemplo con systemd:

# /etc/systemd/system/sysfree-celery.service
# /etc/systemd/system/sysfree-beat.service
# /etc/systemd/system/sysfree-django.service

sudo systemctl enable sysfree-celery sysfree-beat sysfree-django
sudo systemctl start sysfree-celery sysfree-beat sysfree-django
```

## Solución de Problemas

### Problemas Comunes

1. **Celery no inicia**:
   ```bash
   # Verificar Redis
   redis-cli ping
   
   # Verificar configuración
   cd sysfree && python -c "from sysfree import settings; print(settings.CELERY_BROKER_URL)"
   ```

2. **Métricas no aparecen**:
   ```bash
   # Verificar permisos de IP
   curl -H "X-Forwarded-For: 127.0.0.1" http://localhost:8000/metrics/
   ```

3. **Base de datos no conecta**:
   ```bash
   # Verificar conexión
   cd sysfree && python manage.py dbshell
   ```

### Logs Importantes

```bash
# Logs del sistema
tail -f sysfree/logs/sysfree.log

# Logs de errores
tail -f sysfree/logs/error.log

# Logs de seguridad
tail -f sysfree/logs/security.log
```

## Desarrollo y Pruebas

### Pruebas End-to-End

```bash
cd frontend
npm run cypress:open  # Modo interactivo
npm run cypress:run   # Modo headless
```

### Pruebas del Backend

```bash
cd sysfree
python manage.py test

## Facturación Electrónica (Ecuador)

El sistema implementa un pipeline completo para la facturación electrónica, cumpliendo con los requisitos del SRI de Ecuador.

### Arquitectura

El proceso está orquestado a través de una serie de servicios especializados y una tarea asíncrona para garantizar un rendimiento óptimo y un código limpio.

1.  **`VentaService` (`ventas.services`)**: Se encarga de la lógica de negocio para crear y gestionar ventas.
2.  **`ComprobanteService` (`fiscal.services`)**: Contiene la lógica principal para:
    *   **Generar el XML** del comprobante.
    *   **Firmar digitalmente** el XML con el certificado de la empresa.
    *   **Enviar el comprobante al SRI** para su recepción y autorización.
3.  **`sri_utils` (`fiscal.utils`)**: Módulo de utilidades para funciones específicas del SRI, como la generación de la **Clave de Acceso**.
4.  **`RIDEGeneratorService` (`reportes.services`)**: Genera la representación gráfica (RIDE) en formato PDF del comprobante autorizado.
5.  **`procesar_facturacion_electronica_task` (`ventas.tasks`)**: Una tarea asíncrona de Celery que orquesta todo el flujo de trabajo en segundo plano, desde la generación del XML hasta la notificación por correo al cliente.

### Configuración

Para que la facturación electrónica funcione, es necesario configurar los siguientes campos en el panel de administración, dentro del modelo **Empresa** (`/admin/core/empresa/`):

-   **Ambiente de Facturación**: Seleccionar "Pruebas" o "Producción".
-   **Ruta del Certificado P12**: La ruta absoluta en el servidor donde se encuentra almacenado el archivo `.p12` de la firma electrónica.
-   **Clave del Certificado**: La contraseña para acceder al certificado.
-   **URLs de Web Services**: Las URLs para los servicios de recepción y autorización del SRI. Vienen pre-llenadas con los valores por defecto, pero son editables.
```

## Arquitectura del Sistema

```
freecom/
├── sysfree/           # Backend Django
│   ├── core/          # Módulo principal
│   ├── api/           # API REST
│   ├── monitoring/    # Configuración Prometheus
│   └── logs/          # Archivos de log
├── frontend/          # Frontend React
├── env/               # Entorno virtual Python
└── requirements.txt   # Dependencias Python
```

## Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request