import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || '';

// Crear instancia de axios
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token a las peticiones
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
  async (error) => {
    const originalRequest = error.config;
    
    // Si el error es 401 (Unauthorized) y no es un retry
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Intentar refrescar el token
        const refreshToken = localStorage.getItem('refreshToken');
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }
        
        const response = await axios.post(`${API_URL}/api/token/refresh/`, {
          refresh: refreshToken,
        });
        
        const { access } = response.data;
        localStorage.setItem('token', access);
        
        // Reintentar la petición original con el nuevo token
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return axios(originalRequest);
      } catch (refreshError) {
        // Si falla el refresh, limpiar tokens y redirigir al login
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('user');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

// Servicios de autenticación
export const authService = {
  login: (email, password) => api.post('/api/token/', { email, password }),
  register: (userData) => api.post('/api/usuarios/', userData),
  getCurrentUser: () => api.get('/api/usuarios/me/'),
  updateProfile: (userData) => api.put('/api/usuarios/me/', userData),
  changePassword: (passwordData) => api.post('/api/usuarios/change-password/', passwordData),
  refreshToken: (refreshToken) => api.post('/api/token/refresh/', { refresh: refreshToken }),
  forgotPassword: (email) => api.post('/api/password-reset/', { email }),
  resetPassword: (token, password) => api.post(`/api/password-reset/confirm/`, { token, password }),
};

// Servicios de inventario
export const inventarioService = {
  getProductos: (params) => api.get('/api/inventario/productos/', { params }),
  getProducto: (id) => api.get(`/api/inventario/productos/${id}/`),
  createProducto: (data) => api.post('/api/inventario/productos/', data),
  updateProducto: (id, data) => api.put(`/api/inventario/productos/${id}/`, data),
  deleteProducto: (id) => api.delete(`/api/inventario/productos/${id}/`),
  registrarEntrada: (id, data) => api.post(`/api/inventario/productos/${id}/registrar_entrada/`, data),
  registrarSalida: (id, data) => api.post(`/api/inventario/productos/${id}/registrar_salida/`, data),
  
  getCategorias: (params) => api.get('/api/inventario/categorias/', { params }),
  getCategoria: (id) => api.get(`/api/inventario/categorias/${id}/`),
  createCategoria: (data) => api.post('/api/inventario/categorias/', data),
  updateCategoria: (id, data) => api.put(`/api/inventario/categorias/${id}/`, data),
  deleteCategoria: (id) => api.delete(`/api/inventario/categorias/${id}/`),
  
  getProveedores: (params) => api.get('/api/inventario/proveedores/', { params }),
  getProveedor: (id) => api.get(`/api/inventario/proveedores/${id}/`),
  createProveedor: (data) => api.post('/api/inventario/proveedores/', data),
  updateProveedor: (id, data) => api.put(`/api/inventario/proveedores/${id}/`, data),
  deleteProveedor: (id) => api.delete(`/api/inventario/proveedores/${id}/`),
  
  getMovimientos: (params) => api.get('/api/inventario/movimientos/', { params }),
};

// Servicios de clientes
export const clientesService = {
  getClientes: (params) => api.get('/api/clientes/clientes/', { params }),
  getCliente: (id) => api.get(`/api/clientes/clientes/${id}/`),
  createCliente: (data) => api.post('/api/clientes/clientes/', data),
  updateCliente: (id, data) => api.put(`/api/clientes/clientes/${id}/`, data),
  deleteCliente: (id) => api.delete(`/api/clientes/clientes/${id}/`),
  buscarClientes: (termino) => api.get(`/api/clientes/clientes/buscar/?termino=${termino}`),
  
  getDirecciones: (params) => api.get('/api/clientes/direcciones/', { params }),
  getDireccion: (id) => api.get(`/api/clientes/direcciones/${id}/`),
  createDireccion: (data) => api.post('/api/clientes/direcciones/', data),
  updateDireccion: (id, data) => api.put(`/api/clientes/direcciones/${id}/`, data),
  deleteDireccion: (id) => api.delete(`/api/clientes/direcciones/${id}/`),
};

// Servicios de ventas
export const ventasService = {
  getVentas: (params) => api.get('/api/ventas/ventas/', { params }),
  getVenta: (id) => api.get(`/api/ventas/ventas/${id}/`),
  crearVenta: (data) => api.post('/api/ventas/ventas/crear_venta/', data),
  registrarPago: (id, data) => api.post(`/api/ventas/ventas/${id}/registrar_pago/`, data),
  cambiarEstado: (id, data) => api.post(`/api/ventas/ventas/${id}/cambiar_estado/`, data),
  anularVenta: (id, data) => api.post(`/api/ventas/ventas/${id}/anular/`, data),
  
  getPagos: (params) => api.get('/api/ventas/pagos/', { params }),
  getPago: (id) => api.get(`/api/ventas/pagos/${id}/`),
};

// Servicios de reparaciones
export const reparacionesService = {
  getReparaciones: (params) => api.get('/api/reparaciones/reparaciones/', { params }),
  getReparacion: (id) => api.get(`/api/reparaciones/reparaciones/${id}/`),
  createReparacion: (data) => api.post('/api/reparaciones/reparaciones/', data),
  updateReparacion: (id, data) => api.put(`/api/reparaciones/reparaciones/${id}/`, data),
  cambiarEstado: (id, data) => api.post(`/api/reparaciones/reparaciones/${id}/cambiar_estado/`, data),
  registrarDiagnostico: (id, data) => api.post(`/api/reparaciones/reparaciones/${id}/diagnostico/`, data),
  registrarSolucion: (id, data) => api.post(`/api/reparaciones/reparaciones/${id}/solucion/`, data),
  agregarRepuesto: (id, data) => api.post(`/api/reparaciones/reparaciones/${id}/agregar_repuesto/`, data),
};

// Servicios fiscales
export const fiscalService = {
  getAsientos: (params) => api.get('/api/fiscal/asientos/', { params }),
  getAsiento: (id) => api.get(`/api/fiscal/asientos/${id}/`),
  createAsiento: (data) => api.post('/api/fiscal/asientos/', data),
  updateAsiento: (id, data) => api.put(`/api/fiscal/asientos/${id}/`, data),
  deleteAsiento: (id) => api.delete(`/api/fiscal/asientos/${id}/`),
  aprobarAsiento: (id) => api.post(`/api/fiscal/asientos/${id}/aprobar/`),
  anularAsiento: (id, data) => api.post(`/api/fiscal/asientos/${id}/anular/`, data),
  
  getCuentas: (params) => api.get('/api/fiscal/cuentas/', { params }),
  getCuenta: (id) => api.get(`/api/fiscal/cuentas/${id}/`),
  createCuenta: (data) => api.post('/api/fiscal/cuentas/', data),
  updateCuenta: (id, data) => api.put(`/api/fiscal/cuentas/${id}/`, data),
  deleteCuenta: (id) => api.delete(`/api/fiscal/cuentas/${id}/`),
  
  getLibroDiario: (params) => api.get('/api/fiscal/libro-diario/', { params }),
  getLibroMayor: (params) => api.get('/api/fiscal/libro-mayor/', { params }),
  getBalanceGeneral: (params) => api.get('/api/fiscal/balance-general/', { params }),
  getEstadoResultados: (params) => api.get('/api/fiscal/estado-resultados/', { params }),
};

// Servicios de reportes
export const reportesService = {
  generarReporte: (params) => api.get('/api/reportes/generar/', { 
    params,
    responseType: 'blob'
  }),
  getReportesRecientes: () => api.get('/api/reportes/recientes/'),
  getReportesProgramados: () => api.get('/api/reportes/programados/'),
  programarReporte: (data) => api.post('/api/reportes/programar/', data),
  cancelarReporteProgramado: (id) => api.delete(`/api/reportes/programados/${id}/`),
};

// Servicios de tienda online
export const tiendaService = {
  // Productos
  getProductos: (params) => api.get('/api/tienda/productos/', { params }),
  getProducto: (id) => api.get(`/api/tienda/productos/${id}/`),
  getProductosDestacados: () => api.get('/api/tienda/productos/destacados/'),
  getProductosRelacionados: (id) => api.get(`/api/tienda/productos/${id}/relacionados/`),
  valorarProducto: (id, data) => api.post(`/api/tienda/productos/${id}/valorar/`, data),
  
  // Categorías
  getCategorias: () => api.get('/api/tienda/categorias/'),
  getCategoria: (id) => api.get(`/api/tienda/categorias/${id}/`),
  
  // Carrito
  getCarrito: () => api.get('/api/tienda/carrito/'),
  agregarAlCarrito: (data) => api.post('/api/tienda/carrito/agregar/', data),
  actualizarCantidadCarrito: (itemId, data) => api.put(`/api/tienda/carrito/items/${itemId}/`, data),
  eliminarItemCarrito: (itemId) => api.delete(`/api/tienda/carrito/items/${itemId}/`),
  vaciarCarrito: () => api.delete('/api/tienda/carrito/'),
  
  // Cupones
  aplicarCupon: (data) => api.post('/api/tienda/carrito/aplicar-cupon/', data),
  eliminarCupon: () => api.delete('/api/tienda/carrito/cupon/'),
  
  // Favoritos
  getFavoritos: () => api.get('/api/tienda/favoritos/'),
  agregarAFavoritos: (productoId) => api.post('/api/tienda/favoritos/', { producto_id: productoId }),
  eliminarDeFavoritos: (productoId) => api.delete(`/api/tienda/favoritos/${productoId}/`),
  
  // Pedidos
  getPedidos: (params) => api.get('/api/tienda/pedidos/', { params }),
  getPedido: (id) => api.get(`/api/tienda/pedidos/${id}/`),
  crearPedido: (data) => api.post('/api/tienda/pedidos/', data),
  cancelarPedido: (id) => api.post(`/api/tienda/pedidos/${id}/cancelar/`),
  
  // Checkout
  procesarPago: (data) => api.post('/api/tienda/checkout/procesar-pago/', data),
  verificarPago: (id) => api.get(`/api/tienda/checkout/verificar-pago/${id}/`),
};

export default api;