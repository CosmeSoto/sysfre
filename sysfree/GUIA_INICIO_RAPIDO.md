# Guía de inicio rápido para SysFree

Esta guía te ayudará a configurar y ejecutar SysFree en tu entorno local para comenzar a probar el sistema.

## 1. Configuración del entorno

### Requisitos previos
- Python 3.8 o superior
- PostgreSQL 12 o superior
- pip (gestor de paquetes de Python)
- virtualenv (opcional pero recomendado)

### Pasos de instalación

1. **Clonar el repositorio** (si aún no lo has hecho):
   ```bash
   git clone https://github.com/tuusuario/sysfree.git
   cd sysfree
   ```

2. **Crear y activar un entorno virtual**:
   ```bash
   python -m venv env
   source env/bin/activate  # En Windows: env\Scripts\activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**:
   ```bash
   cp .env.example .env
   # Edita el archivo .env con tu configuración
   ```

5. **Crear la base de datos en PostgreSQL**:
   ```bash
   sudo -u postgres psql
   CREATE DATABASE sysfree;
   CREATE USER sysfree_user WITH PASSWORD 'tu_contraseña';
   GRANT ALL PRIVILEGES ON DATABASE sysfree TO sysfree_user;
   \q
   ```

6. **Aplicar migraciones**:
   ```bash
   python manage.py migrate
   ```

7. **Crear un superusuario**:
   ```bash
   python manage.py createsuperuser
   ```

8. **Cargar datos iniciales** (opcional):
   ```bash
   python manage.py loaddata initial_data
   ```

## 2. Ejecutar la aplicación

1. **Iniciar el servidor de desarrollo**:
   ```bash
   python manage.py runserver
   ```

2. **Acceder a la aplicación**:
   - Panel de administración: http://localhost:8000/admin/
   - Aplicación principal: http://localhost:8000/
   - Documentación de la API: http://localhost:8000/api/docs/

## 3. Probar formularios y vistas

### Panel de administración

1. Accede a http://localhost:8000/admin/ con el superusuario creado anteriormente.
2. Explora las diferentes secciones del panel de administración:
   - Usuarios y permisos
   - Clientes
   - Inventario
   - Ventas
   - Reparaciones
   - Contabilidad

### Módulo de clientes

1. Accede a http://localhost:8000/clientes/
2. Prueba las siguientes funcionalidades:
   - Crear un nuevo cliente
   - Ver detalles de un cliente
   - Editar información de un cliente
   - Agregar contactos y direcciones

### Módulo de inventario

1. Accede a http://localhost:8000/inventario/
2. Prueba las siguientes funcionalidades:
   - Crear categorías de productos
   - Crear nuevos productos
   - Actualizar stock
   - Buscar productos

### Módulo de ventas

1. Accede a http://localhost:8000/ventas/
2. Prueba las siguientes funcionalidades:
   - Crear una nueva venta
   - Agregar productos a la venta
   - Aplicar descuentos
   - Finalizar la venta
   - Generar factura

### Módulo de reparaciones

1. Accede a http://localhost:8000/reparaciones/
2. Prueba las siguientes funcionalidades:
   - Crear una nueva orden de reparación
   - Actualizar el estado de la reparación
   - Agregar seguimientos
   - Finalizar la reparación

### API REST

1. Accede a http://localhost:8000/api/docs/
2. Explora los diferentes endpoints disponibles
3. Prueba realizar operaciones a través de la interfaz Swagger

## 4. Solución de problemas comunes

### Error de conexión a la base de datos
- Verifica que PostgreSQL esté en ejecución
- Comprueba las credenciales en el archivo .env
- Asegúrate de que la base de datos exista

### Error al cargar la página
- Verifica que el servidor esté en ejecución
- Comprueba los logs para identificar errores
- Asegúrate de que todas las migraciones se hayan aplicado

### Error al enviar correos
- Verifica la configuración de correo en el archivo .env
- Si usas Gmail, asegúrate de haber generado una contraseña de aplicación
- Comprueba que el servidor SMTP esté accesible

## 5. Próximos pasos

Una vez que te hayas familiarizado con el sistema, puedes:

1. **Personalizar la configuración** según tus necesidades
2. **Crear usuarios adicionales** con diferentes roles y permisos
3. **Explorar la API REST** para integrar con otras aplicaciones
4. **Revisar el código fuente** para entender la estructura y funcionamiento
5. **Contribuir al proyecto** siguiendo la guía de contribución