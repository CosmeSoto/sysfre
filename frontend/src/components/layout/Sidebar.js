import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Nav } from 'react-bootstrap';
import { 
  FaHome, FaBoxes, FaUsers, FaShoppingCart, FaTools, 
  FaFileInvoiceDollar, FaChartBar, FaStore 
} from 'react-icons/fa';
import { useAuth } from '../../context/AuthContext';

const Sidebar = () => {
  const location = useLocation();
  const { currentUser } = useAuth();
  
  // Verificar si la ruta actual coincide con el enlace
  const isActive = (path) => {
    return location.pathname.startsWith(path);
  };

  return (
    <div className="sidebar bg-dark text-white">
      <div className="sidebar-header p-3 text-center">
        <h3>SysFree</h3>
        <p className="text-muted">Sistema de Gestión</p>
      </div>
      
      <Nav className="flex-column">
        <Nav.Item>
          <Link 
            to="/dashboard" 
            className={`nav-link ${isActive('/dashboard') ? 'active' : ''}`}
          >
            <FaHome className="me-2" /> Dashboard
          </Link>
        </Nav.Item>
        
        <Nav.Item>
          <Link 
            to="/inventario" 
            className={`nav-link ${isActive('/inventario') ? 'active' : ''}`}
          >
            <FaBoxes className="me-2" /> Inventario
          </Link>
        </Nav.Item>
        
        <Nav.Item>
          <Link 
            to="/clientes" 
            className={`nav-link ${isActive('/clientes') ? 'active' : ''}`}
          >
            <FaUsers className="me-2" /> Clientes
          </Link>
        </Nav.Item>
        
        <Nav.Item>
          <Link 
            to="/ventas" 
            className={`nav-link ${isActive('/ventas') ? 'active' : ''}`}
          >
            <FaShoppingCart className="me-2" /> Ventas
          </Link>
        </Nav.Item>
        
        <Nav.Item>
          <Link 
            to="/reparaciones" 
            className={`nav-link ${isActive('/reparaciones') ? 'active' : ''}`}
          >
            <FaTools className="me-2" /> Reparaciones
          </Link>
        </Nav.Item>
        
        {currentUser?.is_staff && (
          <>
            <Nav.Item>
              <Link 
                to="/fiscal" 
                className={`nav-link ${isActive('/fiscal') ? 'active' : ''}`}
              >
                <FaFileInvoiceDollar className="me-2" /> Fiscal
              </Link>
            </Nav.Item>
            
            <Nav.Item>
              <Link 
                to="/reportes" 
                className={`nav-link ${isActive('/reportes') ? 'active' : ''}`}
              >
                <FaChartBar className="me-2" /> Reportes
              </Link>
            </Nav.Item>
          </>
        )}
        
        <Nav.Item>
          <Link 
            to="/tienda" 
            className={`nav-link ${isActive('/tienda') ? 'active' : ''}`}
          >
            <FaStore className="me-2" /> E-commerce
          </Link>
        </Nav.Item>
      </Nav>
      
      <div className="sidebar-footer p-3">
        <small className="text-muted">
          &copy; {new Date().getFullYear()} SysFree
        </small>
      </div>
    </div>
  );
};

export default Sidebar;