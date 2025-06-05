import { render, screen } from '@testing-library/react';
import App from '../App';

// Mock de los componentes y contextos
jest.mock('../context/AuthContext', () => ({
  AuthProvider: ({ children }) => children,
  useAuth: () => ({
    currentUser: null,
    loading: false
  })
}));

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  BrowserRouter: ({ children }) => children,
  Routes: ({ children }) => children,
  Route: () => <div />,
  Navigate: () => <div />,
  useNavigate: () => jest.fn()
}));

test('renders without crashing', () => {
  render(<App />);
});