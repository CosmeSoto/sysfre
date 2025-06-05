# SysFree - Sistema de Gestión Empresarial

SysFree es un sistema de gestión empresarial completo que incluye módulos para inventario, ventas, clientes, reparaciones, contabilidad y más.

## Características principales

- **Gestión de inventario**: Control de productos, categorías, proveedores y stock.
- **Gestión de ventas**: Facturación, pedidos, devoluciones y pagos.
- **Gestión de clientes**: Base de datos de clientes, historial y seguimiento.
- **Servicio técnico**: Control de reparaciones, seguimiento y facturación.
- **Contabilidad**: Asientos contables, libro diario, mayor y balances.
- **API REST**: Acceso programático a todas las funcionalidades del sistema.
- **Portal de cliente**: Acceso para clientes a sus facturas, pedidos y reparaciones.

## Requisitos técnicos

- Python 3.8+
- Django 4.0+
- PostgreSQL 12+ (recomendado) o SQLite para desarrollo
- Otras dependencias en requirements.txt

## Instalación

1. Clonar el repositorio:
   ```
   git clone https://github.com/tuusuario/sysfree.git
   cd sysfree
   ```

2. Crear y activar un entorno virtual:
   ```
   python -m venv env
   source env/bin/activate  # En Windows: env\Scripts\activate
   ```

3. Instalar dependencias:
   ```
   pip install -r requirements.txt
   ```

4. Configurar la base de datos:
   ```
   python manage.py migrate
   ```

5. Crear un superusuario:
   ```
   python manage.py createsuperuser
   ```

6. Iniciar el servidor de desarrollo:
   ```
   python manage.py runserver
   ```

## Estructura del proyecto

- **api/**: API REST para acceso programático
- **clientes/**: Gestión de clientes
- **core/**: Funcionalidades centrales del sistema
- **fiscal/**: Gestión contable y fiscal
- **inventario/**: Gestión de productos e inventario
- **reparaciones/**: Gestión de servicio técnico
- **reportes/**: Generación de informes
- **ventas/**: Gestión de ventas y facturación

## Documentación de la API

La API REST está documentada usando Swagger/OpenAPI. Puedes acceder a la documentación en:

- `/api/docs/` - Interfaz Swagger UI
- `/api/redoc/` - Interfaz ReDoc

## Seguridad

El sistema implementa múltiples capas de seguridad:

- Autenticación basada en tokens JWT
- Control de acceso basado en permisos
- Protección contra CSRF
- Limitación de tasa de peticiones
- Registro de actividad y auditoría

## Rendimiento

Para mejorar el rendimiento, el sistema utiliza:

- Caché para consultas frecuentes
- Optimización de consultas a la base de datos
- Paginación de resultados
- Carga diferida de datos

## Contribuir

Si deseas contribuir al proyecto, por favor:

1. Crea un fork del repositorio
2. Crea una rama para tu funcionalidad (`git checkout -b feature/nueva-funcionalidad`)
3. Realiza tus cambios y haz commit (`git commit -am 'Añadir nueva funcionalidad'`)
4. Sube los cambios a tu fork (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## Licencia

Este proyecto está licenciado bajo [Licencia Comercial] - ver el archivo LICENSE para más detalles.