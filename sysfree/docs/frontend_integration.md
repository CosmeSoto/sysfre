# Guía de Integración Frontend - SysFree

Esta guía describe cómo integrar el frontend con la API REST del sistema SysFree.

## Estructura del Proyecto Frontend

```
frontend/
├── public/
│   ├── index.html
│   └── ...
├── src/
│   ├── components/
│   │   ├── auth/
│   │   │   ├── Login.jsx
│   │   │   └── ...
│   │   ├── inventario/
│   │   │   ├── ProductoList.jsx
│   │   │   └── ...
│   │   └── ...
│   ├── services/
│   │   ├── api.js
│   │   └── ...
│   ├── App.js
│   └── index.js
└── package.json
```

## Configuración del Cliente API

El archivo `src/services/api.js` contiene la configuración del cliente Axios para comunicarse con la API:

```javascript
import axios from 'axios';

// Crear instancia de axios con configuración base
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token de autenticación
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para manejar errores de respuesta
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Manejar error de token expirado
    if (error.response && error.response.status === 401) {
      // Intentar refrescar el token
      const refreshToken = localStorage.getItem('refreshToken');
      if (refreshToken) {
        return axios.post('token/refresh/', { refresh: refreshToken })
          .then(response => {
            localStorage.setItem('token', response.data.access);
            
            // Reintentar la solicitud original
            error.config.headers.Authorization = `Bearer ${response.data.access}`;
            return api.request(error.config);
          })
          .catch(refreshError => {
            // Si falla el refresh, cerrar sesión
            localStorage.removeItem('token');
            localStorage.removeItem('refreshToken');
            window.location.href = '/login';
            return Promise.reject(refreshError);
          });
      } else {
        // No hay refresh token, cerrar sesión
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

// Exportar servicios específicos
export const authService = {
  login: (email, password) => api.post('token/', { email, password }),
  refreshToken: (refreshToken) => api.post('token/refresh/', { refresh: refreshToken }),
  getCurrentUser: () => api.get('usuarios/me/'),
};

export const inventarioService = {
  // Métodos para interactuar con la API de inventario
};

// Exportar cliente API por defecto
export default api;
```

## Autenticación

### Componente de Login

El componente `src/components/auth/Login.jsx` maneja la autenticación de usuarios:

```jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../../services/api';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await authService.login(email, password);
      
      // Guardar tokens en localStorage
      localStorage.setItem('token', response.data.access);
      localStorage.setItem('refreshToken', response.data.refresh);
      
      // Obtener información del usuario
      const userResponse = await authService.getCurrentUser();
      localStorage.setItem('user', JSON.stringify(userResponse.data));
      
      // Redirigir al dashboard
      navigate('/dashboard');
    } catch (err) {
      setError(
        err.response?.data?.detail || 
        'Error al iniciar sesión. Por favor, verifica tus credenciales.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Iniciar sesión en SysFree
          </h2>
        </div>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
            <span className="block sm:inline">{error}</span>
          </div>
        )}
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="email-address" className="sr-only">Correo electrónico</label>
              <input
                id="email-address"
                name="email"
                type="email"
                autoComplete="email"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Correo electrónico"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="password" className="sr-only">Contraseña</label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Contraseña"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              {loading ? 'Iniciando sesión...' : 'Iniciar sesión'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Login;
```

### Protección de Rutas

Para proteger las rutas que requieren autenticación, se puede crear un componente `ProtectedRoute`:

```jsx
import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';

const ProtectedRoute = () => {
  const token = localStorage.getItem('token');
  
  if (!token) {
    // Redirigir al login si no hay token
    return <Navigate to="/login" replace />;
  }
  
  // Renderizar las rutas hijas
  return <Outlet />;
};

export default ProtectedRoute;
```

## Integración con Módulos

### Ejemplo: Lista de Productos

El componente `src/components/inventario/ProductoList.jsx` muestra cómo integrar la API de inventario:

```jsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { inventarioService } from '../../services/api';

const ProductoList = () => {
  const [productos, setProductos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    categoria: '',
    estado: '',
    activo: true
  });

  useEffect(() => {
    fetchProductos();
  }, [currentPage, filters]);

  const fetchProductos = async () => {
    setLoading(true);
    try {
      const params = {
        page: currentPage,
        search: searchTerm,
        ...filters
      };
      
      const response = await inventarioService.getProductos(params);
      setProductos(response.data.results);
      setTotalPages(Math.ceil(response.data.count / 10));
    } catch (err) {
      setError('Error al cargar los productos');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Resto del componente...
};

export default ProductoList;
```

## Manejo de Formularios

### Ejemplo: Crear Producto

```jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { inventarioService } from '../../services/api';

const ProductoForm = () => {
  const navigate = useNavigate();
  const [categorias, setCategorias] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    codigo: '',
    nombre: '',
    descripcion: '',
    precio_compra: '',
    precio_venta: '',
    stock: '',
    stock_minimo: '',
    categoria: '',
    estado: 'disponible',
    tipo: 'producto',
    iva: '12.00',
    es_inventariable: true,
    activo: true
  });

  useEffect(() => {
    // Cargar categorías al montar el componente
    const fetchCategorias = async () => {
      try {
        const response = await inventarioService.getCategorias();
        setCategorias(response.data.results);
      } catch (err) {
        console.error('Error al cargar categorías:', err);
      }
    };
    
    fetchCategorias();
  }, []);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      // Convertir valores numéricos
      const dataToSend = {
        ...formData,
        precio_compra: parseFloat(formData.precio_compra),
        precio_venta: parseFloat(formData.precio_venta),
        stock: parseInt(formData.stock),
        stock_minimo: parseInt(formData.stock_minimo),
        iva: parseFloat(formData.iva)
      };
      
      await inventarioService.createProducto(dataToSend);
      navigate('/inventario/productos');
    } catch (err) {
      setError('Error al crear el producto');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Resto del componente...
};

export default ProductoForm;
```

## Manejo de Errores

Para manejar errores de forma consistente, se puede crear un componente `ErrorMessage`:

```jsx
import React from 'react';

const ErrorMessage = ({ error }) => {
  if (!error) return null;
  
  return (
    <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
      <span className="block sm:inline">{error}</span>
    </div>
  );
};

export default ErrorMessage;
```

## Configuración de Variables de Entorno

Crear un archivo `.env` en la raíz del proyecto frontend:

```
REACT_APP_API_URL=http://localhost:8000/api/
REACT_APP_SITE_NAME=SysFree
```

## Optimización de Rendimiento

### Paginación de Datos

Para manejar grandes conjuntos de datos, utilizar la paginación proporcionada por la API:

```jsx
const Pagination = ({ currentPage, totalPages, onPageChange }) => {
  return (
    <div className="flex justify-center mt-6">
      <nav>
        <ul className="flex space-x-2">
          {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
            <li key={page}>
              <button
                onClick={() => onPageChange(page)}
                className={`px-3 py-1 rounded ${
                  currentPage === page
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-200 hover:bg-gray-300'
                }`}
              >
                {page}
              </button>
            </li>
          ))}
        </ul>
      </nav>
    </div>
  );
};
```

### Caché de Datos

Para mejorar el rendimiento, se puede implementar un sistema de caché simple:

```javascript
const cache = {
  data: {},
  timestamp: {},
  
  set(key, data, ttl = 60000) {
    this.data[key] = data;
    this.timestamp[key] = Date.now() + ttl;
  },
  
  get(key) {
    if (this.has(key)) {
      return this.data[key];
    }
    return null;
  },
  
  has(key) {
    return this.data[key] !== undefined && this.timestamp[key] > Date.now();
  },
  
  invalidate(key) {
    delete this.data[key];
    delete this.timestamp[key];
  }
};

// Uso en un servicio
export const categoriaService = {
  getCategorias: async () => {
    const cacheKey = 'categorias';
    
    if (cache.has(cacheKey)) {
      return { data: cache.get(cacheKey) };
    }
    
    const response = await api.get('inventario/categorias/');
    cache.set(cacheKey, response.data, 5 * 60 * 1000); // 5 minutos
    
    return response;
  }
};
```

## Consideraciones de Seguridad

1. **No almacenar información sensible** en localStorage o sessionStorage.
2. **Validar todas las entradas de usuario** antes de enviarlas a la API.
3. **Implementar protección CSRF** para formularios.
4. **Utilizar HTTPS** para todas las comunicaciones con la API.
5. **Sanitizar datos** recibidos de la API antes de mostrarlos en la interfaz.