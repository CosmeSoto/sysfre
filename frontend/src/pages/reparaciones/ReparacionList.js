import React, { useState, useEffect } from 'react';
import { Container, Card, Row, Col, Table, Badge, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { FaPlus, FaEye, FaEdit, FaTools } from 'react-icons/fa';
import { reparacionesService } from '../../services/api';
import SearchBar from '../../components/common/SearchBar';
import Pagination from '../../components/common/Pagination';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import ErrorMessage from '../../components/common/ErrorMessage';
import { formatDate } from '../../utils/formatters';

const ReparacionList = () => {
  const [reparaciones, setReparaciones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [filters, setFilters] = useState({
    estado: '',
    search: ''
  });

  useEffect(() => {
    fetchReparaciones();
  }, [currentPage, filters]);

  const fetchReparaciones = async () => {
    try {
      setLoading(true);
      const params = {
        page: currentPage,
        ...filters
      };
      
      const response = await reparacionesService.getReparaciones(params);
      setReparaciones(response.data.results);
      setTotalPages(Math.ceil(response.data.count / 10));
    } catch (err) {
      setError('Error al cargar las reparaciones');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (searchTerm) => {
    setFilters(prev => ({ ...prev, search: searchTerm }));
    setCurrentPage(1);
  };

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
    setCurrentPage(1);
  };

  const renderEstado = (estado) => {
    switch (estado) {
      case 'recibido':
        return <Badge bg="info">Recibido</Badge>;
      case 'diagnostico':
        return <Badge bg="primary">Diagnóstico</Badge>;
      case 'reparacion':
        return <Badge bg="warning">En Reparación</Badge>;
      case 'espera_repuestos':
        return <Badge bg="secondary">Esperando Repuestos</Badge>;
      case 'terminado':
        return <Badge bg="success">Terminado</Badge>;
      case 'entregado':
        return <Badge bg="dark">Entregado</Badge>;
      case 'cancelado':
        return <Badge bg="danger">Cancelado</Badge>;
      default:
        return <Badge bg="light">{estado}</Badge>;
    }
  };

  if (loading && reparaciones.length === 0) {
    return <LoadingSpinner text="Cargando reparaciones..." />;
  }

  return (
    <Container fluid>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 className="h3">Reparaciones</h1>
        <Link to="/reparaciones/nueva" className="btn btn-primary">
          <FaPlus className="me-2" /> Nueva Reparación
        </Link>
      </div>

      <ErrorMessage error={error} />

      <Card className="mb-4">
        <Card.Header>
          <h5 className="card-title mb-0">Filtros</h5>
        </Card.Header>
        <Card.Body>
          <Row className="g-3">
            <Col md={8}>
              <SearchBar 
                onSearch={handleSearch} 
                placeholder="Buscar por cliente, equipo o número de orden"
                buttonText="Buscar"
              />
            </Col>
            <Col md={4}>
              <label className="form-label">Estado</label>
              <select 
                className="form-select" 
                name="estado" 
                value={filters.estado} 
                onChange={handleFilterChange}
              >
                <option value="">Todos</option>
                <option value="recibido">Recibido</option>
                <option value="diagnostico">Diagnóstico</option>
                <option value="reparacion">En Reparación</option>
                <option value="espera_repuestos">Esperando Repuestos</option>
                <option value="terminado">Terminado</option>
                <option value="entregado">Entregado</option>
                <option value="cancelado">Cancelado</option>
              </select>
            </Col>
          </Row>
        </Card.Body>
      </Card>

      <Card>
        <Card.Body>
          {loading && reparaciones.length > 0 ? (
            <div className="text-center py-3">
              <LoadingSpinner size="sm" centered={false} text="Actualizando..." />
            </div>
          ) : (
            <div className="table-responsive">
              <Table striped hover>
                <thead>
                  <tr>
                    <th>Orden #</th>
                    <th>Cliente</th>
                    <th>Equipo</th>
                    <th>Fecha Recepción</th>
                    <th>Fecha Entrega Est.</th>
                    <th>Estado</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {reparaciones.length > 0 ? (
                    reparaciones.map(reparacion => (
                      <tr key={reparacion.id}>
                        <td>{reparacion.numero_orden}</td>
                        <td>
                          <Link to={`/clientes/${reparacion.cliente.id}`}>
                            {reparacion.cliente.nombres} {reparacion.cliente.apellidos}
                          </Link>
                        </td>
                        <td>{reparacion.equipo}</td>
                        <td>{formatDate(reparacion.fecha_recepcion)}</td>
                        <td>{formatDate(reparacion.fecha_entrega_estimada)}</td>
                        <td>{renderEstado(reparacion.estado)}</td>
                        <td>
                          <div className="btn-group">
                            <Link 
                              to={`/reparaciones/${reparacion.id}`}
                              className="btn btn-sm btn-info"
                              title="Ver detalles"
                            >
                              <FaEye />
                            </Link>
                            <Link 
                              to={`/reparaciones/${reparacion.id}/editar`}
                              className="btn btn-sm btn-warning"
                              title="Editar"
                            >
                              <FaEdit />
                            </Link>
                            <Link 
                              to={`/reparaciones/${reparacion.id}/diagnostico`}
                              className="btn btn-sm btn-primary"
                              title="Diagnóstico"
                            >
                              <FaTools />
                            </Link>
                          </div>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="7" className="text-center py-4">
                        No se encontraron reparaciones
                      </td>
                    </tr>
                  )}
                </tbody>
              </Table>
            </div>
          )}

          <Pagination 
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={setCurrentPage}
          />
        </Card.Body>
      </Card>
    </Container>
  );
};

export default ReparacionList;