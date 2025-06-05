import axios from 'axios';
import api, { authService, inventarioService } from '../../services/api';

// Mock de axios
jest.mock('axios');

describe('API Service', () => {
  beforeEach(() => {
    // Limpiar mocks antes de cada prueba
    jest.clearAllMocks();
    
    // Restaurar localStorage
    localStorage.clear();
  });

  describe('API Client', () => {
    test('should add authorization header when token exists', () => {
      // Configurar token en localStorage
      localStorage.setItem('token', 'fake-token');
      
      // Simular una solicitud
      const requestConfig = {};
      const requestInterceptor = api.interceptors.request.handlers[0].fulfilled;
      
      // Ejecutar el interceptor
      const result = requestInterceptor(requestConfig);
      
      // Verificar que se agregó el encabezado de autorización
      expect(result.headers.Authorization).toBe('Bearer fake-token');
    });

    test('should not add authorization header when token does not exist', () => {
      // Simular una solicitud
      const requestConfig = {};
      const requestInterceptor = api.interceptors.request.handlers[0].fulfilled;
      
      // Ejecutar el interceptor
      const result = requestInterceptor(requestConfig);
      
      // Verificar que no se agregó el encabezado de autorización
      expect(result.headers?.Authorization).toBeUndefined();
    });
  });

  describe('Auth Service', () => {
    test('login should call API with correct parameters', async () => {
      // Configurar mock para simular respuesta exitosa
      axios.post.mockResolvedValueOnce({ data: { access: 'token', refresh: 'refresh' } });
      
      // Llamar al servicio
      const result = await authService.login('test@example.com', 'password123');
      
      // Verificar que se llamó a axios.post con los parámetros correctos
      expect(axios.post).toHaveBeenCalledWith(
        expect.stringContaining('/api/token/'),
        { email: 'test@example.com', password: 'password123' }
      );
      
      // Verificar que se devolvió la respuesta correcta
      expect(result.data).toEqual({ access: 'token', refresh: 'refresh' });
    });

    test('getCurrentUser should call API with correct endpoint', async () => {
      // Configurar mock para simular respuesta exitosa
      axios.get.mockResolvedValueOnce({ data: { id: 1, email: 'test@example.com' } });
      
      // Llamar al servicio
      const result = await authService.getCurrentUser();
      
      // Verificar que se llamó a axios.get con el endpoint correcto
      expect(axios.get).toHaveBeenCalledWith(expect.stringContaining('/api/usuarios/me/'));
      
      // Verificar que se devolvió la respuesta correcta
      expect(result.data).toEqual({ id: 1, email: 'test@example.com' });
    });
  });

  describe('Inventario Service', () => {
    test('getProductos should call API with correct parameters', async () => {
      // Configurar mock para simular respuesta exitosa
      axios.get.mockResolvedValueOnce({ data: { results: [] } });
      
      // Llamar al servicio con parámetros
      const params = { page: 1, search: 'test', categoria: 1 };
      const result = await inventarioService.getProductos(params);
      
      // Verificar que se llamó a axios.get con el endpoint y parámetros correctos
      expect(axios.get).toHaveBeenCalledWith(
        expect.stringContaining('/api/inventario/productos/'),
        { params }
      );
      
      // Verificar que se devolvió la respuesta correcta
      expect(result.data).toEqual({ results: [] });
    });

    test('createProducto should call API with correct data', async () => {
      // Configurar mock para simular respuesta exitosa
      axios.post.mockResolvedValueOnce({ data: { id: 1, nombre: 'Producto Test' } });
      
      // Datos del producto
      const productoData = {
        nombre: 'Producto Test',
        precio_venta: 100,
        categoria: 1
      };
      
      // Llamar al servicio
      const result = await inventarioService.createProducto(productoData);
      
      // Verificar que se llamó a axios.post con el endpoint y datos correctos
      expect(axios.post).toHaveBeenCalledWith(
        expect.stringContaining('/api/inventario/productos/'),
        productoData
      );
      
      // Verificar que se devolvió la respuesta correcta
      expect(result.data).toEqual({ id: 1, nombre: 'Producto Test' });
    });
  });
});