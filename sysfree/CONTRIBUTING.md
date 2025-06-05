# Guía de contribución

¡Gracias por tu interés en contribuir a SysFree! Esta guía te ayudará a configurar el entorno de desarrollo y a entender el proceso de contribución.

## Configuración del entorno de desarrollo

1. **Clonar el repositorio**:
   ```
   git clone https://github.com/tuusuario/sysfree.git
   cd sysfree
   ```

2. **Crear y activar un entorno virtual**:
   ```
   python -m venv env
   source env/bin/activate  # En Windows: env\Scripts\activate
   ```

3. **Instalar dependencias**:
   ```
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**:
   ```
   cp .env.example .env
   # Editar .env con tus configuraciones
   ```

5. **Aplicar migraciones**:
   ```
   python manage.py migrate
   ```

6. **Crear un superusuario**:
   ```
   python manage.py createsuperuser
   ```

7. **Ejecutar el servidor de desarrollo**:
   ```
   python manage.py runserver
   ```

## Flujo de trabajo para contribuciones

1. **Crear una rama**: Crea una rama para tu funcionalidad o corrección.
   ```
   git checkout -b feature/nombre-de-la-funcionalidad
   ```

2. **Realizar cambios**: Implementa tu funcionalidad o corrección.

3. **Ejecutar pruebas**: Asegúrate de que todas las pruebas pasen.
   ```
   python manage.py test
   ```

4. **Formatear código**: Asegúrate de que tu código siga las convenciones de estilo.
   ```
   black .
   flake8
   ```

5. **Hacer commit**: Realiza commits con mensajes descriptivos.
   ```
   git commit -m "Descripción clara del cambio"
   ```

6. **Subir cambios**: Sube tus cambios a tu fork.
   ```
   git push origin feature/nombre-de-la-funcionalidad
   ```

7. **Crear Pull Request**: Crea un Pull Request desde tu fork al repositorio principal.

## Convenciones de código

- Seguimos la guía de estilo PEP 8 para Python.
- Usamos docstrings en formato Google para documentar clases y funciones.
- Los nombres de variables y funciones deben ser descriptivos y en inglés.
- Todas las funciones y clases deben tener pruebas unitarias.

## Estructura del proyecto

- **api/**: API REST para acceso programático
- **clientes/**: Gestión de clientes
- **core/**: Funcionalidades centrales del sistema
- **fiscal/**: Gestión contable y fiscal
- **inventario/**: Gestión de productos e inventario
- **reparaciones/**: Gestión de servicio técnico
- **reportes/**: Generación de informes
- **ventas/**: Gestión de ventas y facturación

## Pruebas

- Todas las funcionalidades deben tener pruebas unitarias.
- Las pruebas se ejecutan con `python manage.py test`.
- Usamos pytest para pruebas más avanzadas.

## Documentación

- Documenta todas las funciones y clases con docstrings.
- Actualiza la documentación de la API cuando añadas o modifiques endpoints.
- Mantén actualizado el archivo README.md con información relevante.

## Preguntas frecuentes

Si tienes alguna pregunta, revisa primero las issues existentes o crea una nueva issue para discutir tu pregunta o problema.