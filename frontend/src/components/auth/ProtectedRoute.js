import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const ProtectedRoute = () => {
  const { currentUser, loading } = useAuth();
  
  // Mostrar un indicador de carga mientras se verifica la autenticación
  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ height: '100vh' }}>
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Cargando...</span>
        </div>
      </div>
    );
  }
  
  // Redirigir al login si no hay usuario autenticado
  if (!currentUser) {
    return <Navigate to="/login" replace />;
  }
  
  // Renderizar las rutas hijas si el usuario está autenticado
  return <Outlet />;
};

export default ProtectedRoute;