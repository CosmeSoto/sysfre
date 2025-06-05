import React, { createContext, useState, useEffect, useContext } from 'react';
import { authService } from '../services/api';
import jwt_decode from 'jwt-decode';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const initAuth = async () => {
      try {
        const token = localStorage.getItem('token');
        if (token) {
          // Verificar si el token ha expirado
          const decodedToken = jwt_decode(token);
          const currentTime = Date.now() / 1000;
          
          if (decodedToken.exp < currentTime) {
            // Token expirado, intentar refresh
            const refreshToken = localStorage.getItem('refreshToken');
            if (refreshToken) {
              try {
                const response = await authService.refreshToken(refreshToken);
                localStorage.setItem('token', response.data.access);
              } catch (error) {
                // Si falla el refresh, limpiar tokens
                logout();
                setError('Sesión expirada. Por favor, inicie sesión nuevamente.');
                setLoading(false);
                return;
              }
            } else {
              logout();
              setLoading(false);
              return;
            }
          }
          
          // Obtener información del usuario
          try {
            const response = await authService.getCurrentUser();
            setCurrentUser(response.data);
          } catch (error) {
            logout();
            setError('Error al obtener información del usuario.');
          }
        }
      } catch (error) {
        console.error('Error en la inicialización de autenticación:', error);
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async (email, password) => {
    try {
      setError(null);
      const response = await authService.login(email, password);
      localStorage.setItem('token', response.data.access);
      localStorage.setItem('refreshToken', response.data.refresh);
      
      const userResponse = await authService.getCurrentUser();
      setCurrentUser(userResponse.data);
      return userResponse.data;
    } catch (error) {
      setError(
        error.response?.data?.detail || 
        'Error al iniciar sesión. Verifique sus credenciales.'
      );
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
    setCurrentUser(null);
  };

  const updateProfile = async (userData) => {
    try {
      setError(null);
      const response = await authService.updateProfile(userData);
      setCurrentUser(response.data);
      return response.data;
    } catch (error) {
      setError(
        error.response?.data?.detail || 
        'Error al actualizar el perfil.'
      );
      throw error;
    }
  };

  const value = {
    currentUser,
    loading,
    error,
    login,
    logout,
    updateProfile,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};