# SysFree - Sistema de Gestión Empresarial

SysFree es un sistema completo de gestión empresarial que incluye módulos de inventario, ventas, clientes, reparaciones, contabilidad y tienda online.

## Características

- **Inventario**: Gestión de productos, categorías y proveedores
- **Ventas**: Creación de ventas, facturación y seguimiento de pagos
- **Clientes**: Gestión de clientes y sus datos de contacto
- **Reparaciones**: Seguimiento de órdenes de reparación y diagnósticos
- **Contabilidad**: Asientos contables y plan de cuentas
- **Reportes**: Generación de informes personalizados
- **Tienda Online**: Catálogo de productos y carrito de compras

## Requisitos

- Node.js 14+
- Python 3.8+
- PostgreSQL 12+

## Instalación

### Backend

```bash
cd sysfree/backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend

```bash
cd sysfree/frontend
npm install
npm start
```

## Uso

Accede a la aplicación en http://localhost:3000

Usuario: admin@example.com
Contraseña: la que configuraste al crear el superusuario

## Pruebas

### Pruebas End-to-End

Para ejecutar las pruebas end-to-end con Cypress:

```bash
cd sysfree/frontend
npm run cypress:open  # Modo interactivo
npm run cypress:run   # Modo headless
```

## Optimizaciones

El sistema incluye las siguientes optimizaciones:

- Lazy loading para componentes grandes
- Memoización para evitar renderizados innecesarios
- Carga diferida de imágenes
- Componentes accesibles según estándares WCAG