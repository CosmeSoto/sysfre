import React, { lazy, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

// Contexto
import { AuthProvider } from './context/AuthContext';

// Layout
import Layout from './components/layout/Layout';

// Componente para rutas protegidas
import ProtectedRoute from './components/auth/ProtectedRoute';

// Componente de carga
const LoadingSpinner = () => (
  <div className="d-flex justify-content-center align-items-center" style={{ height: '100vh' }}>
    <div className="spinner-border" role="status">
      <span className="visually-hidden">Cargando...</span>
    </div>
  </div>
);

// Páginas de autenticación
const Login = lazy(() => import('./pages/auth/Login'));
const ForgotPassword = lazy(() => import('./pages/auth/ForgotPassword'));
const ResetPassword = lazy(() => import('./pages/auth/ResetPassword'));

// Páginas principales
const Dashboard = lazy(() => import('./pages/dashboard/Dashboard'));

// Páginas de inventario
const ProductoList = lazy(() => import('./pages/inventario/ProductoList'));
const ProductoDetail = lazy(() => import('./pages/inventario/ProductoDetail'));
const ProductoForm = lazy(() => import('./pages/inventario/ProductoForm'));
const CategoriaList = lazy(() => import('./pages/inventario/CategoriaList'));
const CategoriaForm = lazy(() => import('./pages/inventario/CategoriaForm'));
const ProveedorList = lazy(() => import('./pages/inventario/ProveedorList'));
const ProveedorDetail = lazy(() => import('./pages/inventario/ProveedorDetail'));
const ProveedorForm = lazy(() => import('./pages/inventario/ProveedorForm'));

// Páginas de clientes
const ClienteList = lazy(() => import('./pages/clientes/ClienteList'));
const ClienteDetail = lazy(() => import('./pages/clientes/ClienteDetail'));
const ClienteForm = lazy(() => import('./pages/clientes/ClienteForm'));

// Páginas de ventas
const VentaList = lazy(() => import('./pages/ventas/VentaList'));
const VentaDetail = lazy(() => import('./pages/ventas/VentaDetail'));
const VentaForm = lazy(() => import('./pages/ventas/VentaForm'));
const PagoForm = lazy(() => import('./pages/ventas/PagoForm'));

// Páginas de reparaciones
const ReparacionList = lazy(() => import('./pages/reparaciones/ReparacionList'));
const ReparacionDetail = lazy(() => import('./pages/reparaciones/ReparacionDetail'));
const ReparacionForm = lazy(() => import('./pages/reparaciones/ReparacionForm'));

// Páginas fiscales
const AsientoList = lazy(() => import('./pages/fiscal/AsientoList'));
const CuentaList = lazy(() => import('./pages/fiscal/CuentaList'));

// Páginas de reportes
const ReporteList = lazy(() => import('./pages/reportes/ReporteList'));

// Páginas de tienda online
const TiendaHome = lazy(() => import('./pages/tienda/TiendaHome'));
const ProductoDetalle = lazy(() => import('./pages/tienda/ProductoDetalle'));
const Carrito = lazy(() => import('./pages/tienda/Carrito'));

function App() {
  return (
    <AuthProvider>
      <Router>
        <ToastContainer position="top-right" autoClose={3000} />
        <Suspense fallback={<LoadingSpinner />}>
          <Routes>
            {/* Rutas públicas */}
            <Route path="/login" element={<Login />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password/:token" element={<ResetPassword />} />
            
            {/* Rutas de tienda online (públicas) */}
            <Route path="/tienda" element={<Layout />}>
              <Route index element={<TiendaHome />} />
              <Route path="productos/:id" element={<ProductoDetalle />} />
              <Route path="carrito" element={<Carrito />} />
            </Route>
            
            {/* Rutas protegidas */}
            <Route path="/" element={<ProtectedRoute />}>
              <Route element={<Layout />}>
                <Route index element={<Navigate to="/dashboard" replace />} />
                <Route path="/dashboard" element={<Dashboard />} />
                
                {/* Rutas de inventario */}
                <Route path="/inventario">
                  <Route index element={<Navigate to="/inventario/productos" replace />} />
                  <Route path="productos" element={<ProductoList />} />
                  <Route path="productos/nuevo" element={<ProductoForm />} />
                  <Route path="productos/:id" element={<ProductoDetail />} />
                  <Route path="productos/:id/editar" element={<ProductoForm />} />
                  
                  <Route path="categorias" element={<CategoriaList />} />
                  <Route path="categorias/nueva" element={<CategoriaForm />} />
                  <Route path="categorias/:id/editar" element={<CategoriaForm />} />
                  
                  <Route path="proveedores" element={<ProveedorList />} />
                  <Route path="proveedores/nuevo" element={<ProveedorForm />} />
                  <Route path="proveedores/:id" element={<ProveedorDetail />} />
                  <Route path="proveedores/:id/editar" element={<ProveedorForm />} />
                </Route>
                
                {/* Rutas de clientes */}
                <Route path="/clientes">
                  <Route index element={<ClienteList />} />
                  <Route path="nuevo" element={<ClienteForm />} />
                  <Route path=":id" element={<ClienteDetail />} />
                  <Route path=":id/editar" element={<ClienteForm />} />
                </Route>
                
                {/* Rutas de ventas */}
                <Route path="/ventas">
                  <Route index element={<VentaList />} />
                  <Route path="nueva" element={<VentaForm />} />
                  <Route path=":id" element={<VentaDetail />} />
                  <Route path=":id/pago" element={<PagoForm />} />
                </Route>
                
                {/* Rutas de reparaciones */}
                <Route path="/reparaciones">
                  <Route index element={<ReparacionList />} />
                  <Route path="nueva" element={<ReparacionForm />} />
                  <Route path=":id" element={<ReparacionDetail />} />
                  <Route path=":id/editar" element={<ReparacionForm />} />
                  <Route path=":id/diagnostico" element={<ReparacionForm />} />
                  <Route path=":id/solucion" element={<ReparacionForm />} />
                  <Route path=":id/repuestos" element={<ReparacionForm />} />
                </Route>
                
                {/* Rutas fiscales */}
                <Route path="/fiscal">
                  <Route index element={<Navigate to="/fiscal/asientos" replace />} />
                  <Route path="asientos" element={<AsientoList />} />
                  <Route path="cuentas" element={<CuentaList />} />
                </Route>
                
                {/* Rutas de reportes */}
                <Route path="/reportes">
                  <Route index element={<ReporteList />} />
                </Route>
              </Route>
            </Route>
            
            {/* Ruta para 404 */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </Suspense>
      </Router>
    </AuthProvider>
  );
}

export default App;