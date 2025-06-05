import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Form, Button, Table, Badge, Pagination } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { FaPlus, FaSearch, FaEye, FaPrint, FaFileInvoice } from 'react-icons/fa';
import { ventasService } from '../../services/api';

const VentaList = () => {
  const [ventas, setVentas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Estado para filtros y paginación
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    tipo: '',
    estado: '',
    fecha_inicio: '',
    fecha_fin: ''
  });
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);

  // Cargar ventas al montar el componente
  useEffect(() => {
    fetchVentas();
  }, [currentPage, filters]);

  // Función para cargar ventas
  const fetchVentas = async () => {
    try {
      setLoading(true);
      
      const params = {
        page: currentPage,
        search: searchTerm,
        ...filters
      };
      
      const response = await ventasService.getVentas(params);
      setVentas(response.data.results);
      setTotalPages(Math.ceil(response.data.count / 10));
    } catch (err) {
      setError('Error al cargar las ventas');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Manejar cambios en los filtros
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
    setCurrentPage(1);
  };

  // Manejar búsqueda
  const handleSearch = (e) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchVentas();
  };

  // Manejar cambio de página
  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  // Renderizar estado de la venta
  const renderEstado = (estado) => {
    switch (estado) {
      case 'pagado':
        return <Badge bg="success">Pagado</Badge>;
      case 'pendiente':
        return <Badge bg="warning">Pendiente</Badge>;
      case 'anulado':
        return <Badge bg="danger">Anulado</Badge>;
      case 'borrador':
        return <Badge bg="secondary">Borrador</Badge>;
      default:
        return <Badge bg="info">{estado}</Badge>;
    }
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

  if (loading && ventas.length === 0) {
    return (
      <Container>
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Cargando...</span>
          </div>
          <p className="mt-3">Cargando ventas...</p>
        </div>
      </Container>
    );
  }

  return (
    <Container fluid>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 className="h3">Ventas</h1>
        <Link to="/ventas/nueva" className="btn btn-primary">
          <FaPlus className="me-2" /> Nueva Venta
        </Link>
      </div>
      
      {error && (
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      )}
      
      <Card className="mb-4">
        <Card.Header>
          <h5 className="card-title mb-0">Filtros</h5>
        </Card.Header>
        <Card.Body>
          <Form onSubmit={handleSearch}>
            <Row className="g-3">
              <Col md={3}>
                <Form.Group>
                  <Form.Label>Buscar</Form.Label>
                  <Form.Control
                    type="text"
                    placeholder="Número o cliente"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </Form.Group>
              </Col>
              
              <Col md={3}>
                <Form.Group>
                  <Form.Label>Tipo</Form.Label>
                  <Form.Select
                    name="tipo"
                    value={filters.tipo}
                    onChange={handleFilterChange}
                  >
                    <option value="">Todos</option>
                    <option value="factura">Factura</option>
                    <option value="nota_venta">Nota de Venta</option>
                  </Form.Select>
                </Form.Group>
              </Col>
              
              <Col md={3}>
                <Form.Group>
                  <Form.Label>Estado</Form.Label>
                  <Form.Select
                    name="estado"
                    value={filters.estado}
                    onChange={handleFilterChange}
                  >
                    <option value="">Todos</option>
                    <option value="borrador">Borrador</option>
                    <option value="pendiente">Pendiente</option>
                    <option value="pagado">Pagado</option>
                    <option value="anulado">Anulado</option>
                  </Form.Select>
                </Form.Group>
              </Col>
              
              <Col md={3} className="d-flex align-items-end">
                <Button type="submit" variant="primary" className="w-100">
                  <FaSearch className="me-2" /> Filtrar
                </Button>
              </Col>
            </Row>
            
            <Row className="mt-3">
              <Col md={3}>
                <Form.Group>
                  <Form.Label>Fecha Inicio</Form.Label>
                  <Form.Control
                    type="date"
                    name="fecha_inicio"
                    value={filters.fecha_inicio}
                    onChange={handleFilterChange}
                  />
                </Form.Group>
              </Col>
              
              <Col md={3}>
                <Form.Group>
                  <Form.Label>Fecha Fin</Form.Label>
                  <Form.Control
                    type="date"
                    name="fecha_fin"
                    value={filters.fecha_fin}
                    onChange={handleFilterChange}
                  />
                </Form.Group>
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
                  <th>Número</th>
                  <th>Fecha</th>
                  <th>Cliente</th>
                  <th>Tipo</th>
                  <th>Subtotal</th>
                  <th>IVA</th>
                  <th>Total</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {ventas.length > 0 ? (
                  ventas.map(venta => (
                    <tr key={venta.id}>
                      <td>{venta.numero}</td>
                      <td>{new Date(venta.fecha).toLocaleDateString()}</td>
                      <td>
                        <Link to={`/clientes/${venta.cliente}`}>
                          {venta.cliente_nombre}
                        </Link>
                      </td>
                      <td>
                        <Badge bg="info">
                          {venta.tipo === 'factura' ? 'Factura' : 'Nota de Venta'}
                        </Badge>
                      </td>
                      <td>${venta.subtotal.toFixed(2)}</td>
                      <td>${venta.iva.toFixed(2)}</td>
                      <td>${venta.total.toFixed(2)}</td>
                      <td>{renderEstado(venta.estado)}</td>
                      <td>
                        <div className="btn-group">
                          <Link 
                            to={`/ventas/${venta.id}`}
                            className="btn btn-sm btn-info"
                            title="Ver detalles"
                          >
                            <FaEye />
                          </Link>
                          <Link 
                            to={`/ventas/${venta.id}/imprimir`}
                            className="btn btn-sm btn-secondary"
                            title="Imprimir"
                          >
                            <FaPrint />
                          </Link>
                          <Link 
                            to={`/ventas/${venta.id}/factura`}
                            className="btn btn-sm btn-primary"
                            title="Ver factura"
                          >
                            <FaFileInvoice />
                          </Link>
                        </div>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="9" className="text-center py-4">
                      No se encontraron ventas
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

export default VentaList;