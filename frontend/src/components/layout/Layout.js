import React from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import Header from './Header';
import Sidebar from './Sidebar';
import { useAuth } from '../../context/AuthContext';

const Layout = ({ children }) => {
  const { currentUser } = useAuth();

  // Si no hay usuario autenticado, solo mostrar el contenido sin layout
  if (!currentUser) {
    return <>{children}</>;
  }

  return (
    <div className="layout d-flex flex-column min-vh-100">
      <Header />
      <Container fluid className="flex-grow-1">
        <Row className="h-100">
          <Col md={3} lg={2} className="sidebar-col p-0">
            <Sidebar />
          </Col>
          <Col md={9} lg={10} className="content-col py-3">
            {children}
          </Col>
        </Row>
      </Container>
      <footer className="bg-light text-center py-3">
        <Container>
          <small className="text-muted">
            &copy; {new Date().getFullYear()} SysFree - Sistema de Gestión
          </small>
        </Container>
      </footer>
    </div>
  );
};

export default Layout;