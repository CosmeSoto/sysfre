# SysFree Frontend

Este es el frontend para el sistema SysFree, desarrollado con React.

## Requisitos

- Node.js 16+
- npm 8+

## Instalación

1. Clonar el repositorio
2. Instalar dependencias:

```bash
cd sysfree/frontend
npm install
```

## Configuración

Crear un archivo `.env` en la raíz del proyecto con las siguientes variables:

```
REACT_APP_API_URL=http://localhost:8000
```

## Desarrollo

Para iniciar el servidor de desarrollo:

```bash
npm start
```

La aplicación estará disponible en [http://localhost:3000](http://localhost:3000).

## Construcción

Para construir la aplicación para producción:

```bash
npm run build
```

Los archivos se generarán en la carpeta `build`.

## Estructura del Proyecto

```
src/
├── components/       # Componentes reutilizables
│   ├── auth/         # Componentes de autenticación
│   ├── layout/       # Componentes de layout
│   └── ...
├── context/          # Contextos de React
├── hooks/            # Hooks personalizados
├── pages/            # Páginas de la aplicación
│   ├── auth/         # Páginas de autenticación
│   ├── dashboard/    # Páginas del dashboard
│   └── ...
├── services/         # Servicios para comunicación con la API
├── utils/            # Utilidades y funciones auxiliares
├── App.js            # Componente principal
└── index.js          # Punto de entrada
```

## Tecnologías Utilizadas

- React 18
- React Router 6
- Bootstrap 5
- Axios
- Formik
- Chart.js
- React Icons