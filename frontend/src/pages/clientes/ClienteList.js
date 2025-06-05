import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Form, Button, Table, Badge, Pagination } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { FaPlus, FaSearch, FaEye, FaEdit, FaTrash } from 'react-icons/fa';
import { clientesService } from '../../services/api';

const ClienteList = () => {
  const [clientes, setClientes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Estado para filtros y paginación
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);

  // Cargar clientes al montar el componente
  useEffect(() => {
    fetchClientes();
  }, [currentPage]);

  // Función para cargar clientes
  const fetchClientes = async () => {
    try {
      setLoading(true);
      
      const params = {
        page: currentPage,
        search: searchTerm
      };
      
      const response = await clientesService.getClientes(params);
      setClientes(response.data.results);
      setTotalPages(Math.ceil(response.data.count / 10));
    } catch (err) {
      setError('Error al cargar los clientes');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Manejar búsqueda
  const handleSearch = (e) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchClientes();
  };

  // Manejar cambio de página
  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  // Renderizar paginación
  const renderPagination = () => {
    if (totalPages <= 1) return null;
    
    const pages = [];
    for (let i = 1; i <= totalPages; i++) {
      if (
        i === 1 || 
        i === totalPages || 
        (i >= currentPage - 2 && i <= currentPage + 2)
      ) {
        pages.push(
          <Pagination.Item 
            key={i} 
            active={i === currentPage}
            onClick={() => handlePageChange(i)}
          >
            {i}
          </Pagination.Item>
        );
      } else if (
        i === currentPage - 3 || 
        i === currentPage + 3
      ) {
        pages.push(<Pagination.Ellipsis key={`ellipsis-${i}`} />);
      }
    }
    
    return (
      <Pagination className="justify-content-center mt-4">
        <Pagination.First 
          onClick={() => handlePageChange(1)} 
          disabled={currentPage === 1}
        />
        <Pagination.Prev 
          onClick={() => handlePageChange(currentPage - 1)} 
          disabled={currentPage === 1}
        />
        
        {pages}
        
        <Pagination.Next 
          onClick={() => handlePageChange(currentPage + 1)} 
          disabled={currentPage === totalPages}
        />
        <Pagination.Last 
          onClick={() => handlePageChange(totalPages)} 
          disabled={currentPage === totalPages}
        />
      </Pagination>
    );
  };

  if (loading && clientes.length === 0) {
    return (
      <Container>
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Cargando...</span>
          </div>
          <p className="mt-3">Cargando clientes...</p>
        </div>
      </Container>
    );
  }

  return (
    <Container fluid>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 className="h3">Clientes</h1>
        <Link to="/clientes/nuevo" className="btn btn-primary">
          <FaPlus className="me-2" /> Nuevo Cliente
        </Link>
      </div>
      
      {error && (
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      )}
      
      <Card className="mb-4">
        <Card.Header>
          <h5 className="card-title mb-0">Buscar</h5>
        </Card.Header>
        <Card.Body>
          <Form onSubmit={handleSearch}>
            <Row className="g-3">
              <Col md={10}>
                <Form.Control
                  type="text"
                  placeholder="Buscar por nombre, identificación o email"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </Col>
              <Col md={2}>
                <Button type="submit" variant="primary" className="w-100">
                  <FaSearch className="me-2" /> Buscar
                </Button>
              </Col>
            </Row>
          </Form>
        </Card.Body>
      </Card>
      
      <Card>
        <Card.Body>
          <div className="table-responsive">
            <Table striped hover>
              <thead>
                <tr>
                  <th>Identificación</th>
                  <th>Nombres</th>
                  <th>Apellidos</th>
                  <th>Email</th>
                  <th>Teléfono</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {clientes.length > 0 ? (
                  clientes.map(cliente => (
                    <tr key={cliente.id}>
                      <td>
                        <Badge bg="secondary" className="me-1">
                          {cliente.tipo_identificacion}
                        </Badge>
                        {cliente.identificacion}
                      </td>
                      <td>{cliente.nombres}</td>
                      <td>{cliente.apellidos}</td>
                      <td>{cliente.email}</td>
                      <td>{cliente.telefono}</td>
                      <td>
                        <div className="btn-group">
                          <Link 
                            to={`/clientes/${cliente.id}`}
                            className="btn btn-sm btn-info"
                            title="Ver detalles"
                          >
                            <FaEye />
                          </Link>
                          <Link 
                            to={`/clientes/${cliente.id}/editar`}
                            className="btn btn-sm btn-warning"
                            title="Editar"
                          >
                            <FaEdit />
                          </Link>
                          <Link 
                            to={`/clientes/${cliente.id}/eliminar`}
                            className="btn btn-sm btn-danger"
                            title="Eliminar"
                          >
                            <FaTrash />
                          </Link>
                        </div>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="6" className="text-center py-4">
                      No se encontraron clientes
                    </td>
                  </tr>
                )}
              </tbody>
            </Table>
          </div>
          
          {renderPagination()}
        </Card.Body>
      </Card>
    </Container>
  );
};

export default ClienteList;