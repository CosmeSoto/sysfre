import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Login from '../../pages/auth/Login';
import { authService } from '../../services/api';

// Mock de los servicios y hooks
jest.mock('../../services/api', () => ({
  authService: {
    login: jest.fn(),
    getCurrentUser: jest.fn()
  }
}));

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
  Link: ({ children, to }) => <a href={to}>{children}</a>
}));

describe('Login Component', () => {
  beforeEach(() => {
    // Limpiar mocks antes de cada prueba
    jest.clearAllMocks();
  });

  test('renders login form', () => {
    render(<Login />);
    
    // Verificar que los elementos del formulario estén presentes
    expect(screen.getByLabelText(/correo electrónico/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/contraseña/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /iniciar sesión/i })).toBeInTheDocument();
    expect(screen.getByText(/¿olvidó su contraseña\?/i)).toBeInTheDocument();
  });

  test('shows validation errors for empty fields', async () => {
    render(<Login />);
    
    // Enviar formulario sin datos
    fireEvent.click(screen.getByRole('button', { name: /iniciar sesión/i }));
    
    // Verificar mensajes de error
    await waitFor(() => {
      expect(screen.getByText(/el correo electrónico es requerido/i)).toBeInTheDocument();
      expect(screen.getByText(/la contraseña es requerida/i)).toBeInTheDocument();
    });
  });

  test('shows validation error for invalid email', async () => {
    render(<Login />);
    
    // Ingresar email inválido
    fireEvent.change(screen.getByLabelText(/correo electrónico/i), {
      target: { value: 'invalid-email' }
    });
    
    // Ingresar contraseña
    fireEvent.change(screen.getByLabelText(/contraseña/i), {
      target: { value: 'password123' }
    });
    
    // Enviar formulario
    fireEvent.click(screen.getByRole('button', { name: /iniciar sesión/i }));
    
    // Verificar mensaje de error
    await waitFor(() => {
      expect(screen.getByText(/ingrese un correo electrónico válido/i)).toBeInTheDocument();
    });
  });

  test('calls login service with correct credentials', async () => {
    // Configurar mock para simular login exitoso
    authService.login.mockResolvedValueOnce({
      data: { access: 'fake-token', refresh: 'fake-refresh-token' }
    });
    
    authService.getCurrentUser.mockResolvedValueOnce({
      data: { id: 1, email: 'test@example.com', nombres: 'Test', apellidos: 'User' }
    });
    
    render(<Login />);
    
    // Ingresar credenciales válidas
    fireEvent.change(screen.getByLabelText(/correo electrónico/i), {
      target: { value: 'test@example.com' }
    });
    
    fireEvent.change(screen.getByLabelText(/contraseña/i), {
      target: { value: 'password123' }
    });
    
    // Enviar formulario
    fireEvent.click(screen.getByRole('button', { name: /iniciar sesión/i }));
    
    // Verificar que se llamó al servicio con las credenciales correctas
    await waitFor(() => {
      expect(authService.login).toHaveBeenCalledWith('test@example.com', 'password123');
      expect(authService.getCurrentUser).toHaveBeenCalled();
    });
  });

  test('shows error message on login failure', async () => {
    // Configurar mock para simular error de login
    authService.login.mockRejectedValueOnce({
      response: { data: { detail: 'Credenciales inválidas' } }
    });
    
    render(<Login />);
    
    // Ingresar credenciales
    fireEvent.change(screen.getByLabelText(/correo electrónico/i), {
      target: { value: 'test@example.com' }
    });
    
    fireEvent.change(screen.getByLabelText(/contraseña/i), {
      target: { value: 'wrong-password' }
    });
    
    // Enviar formulario
    fireEvent.click(screen.getByRole('button', { name: /iniciar sesión/i }));
    
    // Verificar mensaje de error
    await waitFor(() => {
      expect(screen.getByText(/credenciales inválidas/i)).toBeInTheDocument();
    });
  });
});