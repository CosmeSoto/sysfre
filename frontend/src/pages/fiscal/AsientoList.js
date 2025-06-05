import React, { useState, useEffect } from 'react';
import { Container, Card, Row, Col, Table, Badge, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { FaPlus, FaEye, FaEdit, FaTrash } from 'react-icons/fa';
import { fiscalService } from '../../services/api';
import SearchBar from '../../components/common/SearchBar';
import Pagination from '../../components/common/Pagination';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import ErrorMessage from '../../components/common/ErrorMessage';
import { formatDate, formatCurrency } from '../../utils/formatters';

const AsientoList = () => {
  const [asientos, setAsientos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [filters, setFilters] = useState({
    fecha_inicio: '',
    fecha_fin: '',
    tipo: '',
    search: ''
  });

  useEffect(() => {
    fetchAsientos();
  }, [currentPage, filters]);

  const fetchAsientos = async () => {
    try {
      setLoading(true);
      const params = {
        page: currentPage,
        ...filters
      };
      
      const response = await fiscalService.getAsientos(params);
      setAsientos(response.data.results);
      setTotalPages(Math.ceil(response.data.count / 10));
    } catch (err) {
      setError('Error al cargar los asientos contables');
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
      case 'borrador':
        return <Badge bg="secondary">Borrador</Badge>;
      case 'aprobado':
        return <Badge bg="success">Aprobado</Badge>;
      case 'anulado':
        return <Badge bg="danger">Anulado</Badge>;
      default:
        return <Badge bg="light">{estado}</Badge>;
    }
  };

  if (loading && asientos.length === 0) {
    return <LoadingSpinner text="Cargando asientos contables..." />;
  }

  return (
    <Container fluid>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 className="h3">Asientos Contables</h1>
        <Link to="/fiscal/asientos/nuevo" className="btn btn-primary">
          <FaPlus className="me-2" /> Nuevo Asiento
        </Link>
      </div>

      <ErrorMessage error={error} />

      <Card className="mb-4">
        <Card.Header>
          <h5 className="card-title mb-0">Filtros</h5>
        </Card.Header>
        <Card.Body>
          <Row className="g-3">
            <Col md={6}>
              <SearchBar 
                onSearch={handleSearch} 
                placeholder="Buscar por número, descripción o referencia"
                buttonText="Buscar"
              />
            </Col>
            <Col md={6}>
              <Row>
                <Col md={6}>
                  <label className="form-label">Tipo</label>
                  <select 
                    className="form-select" 
                    name="tipo" 
                    value={filters.tipo} 
                    onChange={handleFilterChange}
                  >
                    <option value="">Todos</option>
                    <option value="venta">Venta</option>
                    <option value="compra">Compra</option>
                    <option value="gasto">Gasto</option>
                    <option value="ajuste">Ajuste</option>
                    <option value="manual">Manual</option>
                  </select>
                </Col>
                <Col md={6}>
                  <label className="form-label">Estado</label>
                  <select 
                    className="form-select" 
                    name="estado" 
                    value={filters.estado} 
                    onChange={handleFilterChange}
                  >
                    <option value="">Todos</option>
                    <option value="borrador">Borrador</option>
                    <option value="aprobado">Aprobado</option>
                    <option value="anulado">Anulado</option>
                  </select>
                </Col>
              </Row>
            </Col>
          </Row>
          
          <Row className="mt-3">
            <Col md={6}>
              <Row>
                <Col md={6}>
                  <label className="form-label">Fecha Inicio</label>
                  <input 
                    type="date" 
                    className="form-control" 
                    name="fecha_inicio" 
                    value={filters.fecha_inicio} 
                    onChange={handleFilterChange}
                  />
                </Col>
                <Col md={6}>
                  <label className="form-label">Fecha Fin</label>
                  <input 
                    type="date" 
                    className="form-control" 
                    name="fecha_fin" 
                    value={filters.fecha_fin} 
                    onChange={handleFilterChange}
                  />
                </Col>
              </Row>
            </Col>
            <Col md={6} className="d-flex align-items-end">
              <Button 
                variant="secondary" 
                className="w-100"
                onClick={() => {
                  setFilters({
                    fecha_inicio: '',
                    fecha_fin: '',
                    tipo: '',
                    estado: '',
                    search: ''
                  });
                  setCurrentPage(1);
                }}
              >
                Limpiar Filtros
              </Button>
            </Col>
          </Row>
        </Card.Body>
      </Card>

      <Card>
        <Card.Body>
          {loading && asientos.length > 0 ? (
            <div className="text-center py-3">
              <LoadingSpinner size="sm" centered={false} text="Actualizando..." />
            </div>
          ) : (
            <div className="table-responsive">
              <Table striped hover>
                <thead>
                  <tr>
                    <th>Número</th>
                    <th>Fecha</th>
                    <th>Tipo</th>
                    <th>Descripción</th>
                    <th>Referencia</th>
                    <th>Debe</th>
                    <th>Haber</th>
                    <th>Estado</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {asientos.length > 0 ? (
                    asientos.map(asiento => (
                      <tr key={asiento.id}>
                        <td>{asiento.numero}</td>
                        <td>{formatDate(asiento.fecha)}</td>
                        <td>{asiento.tipo}</td>
                        <td>{asiento.descripcion}</td>
                        <td>{asiento.referencia}</td>
                        <td>{formatCurrency(asiento.total_debe)}</td>
                        <td>{formatCurrency(asiento.total_haber)}</td>
                        <td>{renderEstado(asiento.estado)}</td>
                        <td>
                          <div className="btn-group">
                            <Link 
                              to={`/fiscal/asientos/${asiento.id}`}
                              className="btn btn-sm btn-info"
                              title="Ver detalles"
                            >
                              <FaEye />
                            </Link>
                            {asiento.estado === 'borrador' && (
                              <Link 
                                to={`/fiscal/asientos/${asiento.id}/editar`}
                                className="btn btn-sm btn-warning"
                                title="Editar"
                              >
                                <FaEdit />
                              </Link>
                            )}
                            {asiento.estado === 'borrador' && (
                              <Link 
                                to={`/fiscal/asientos/${asiento.id}/eliminar`}
                                className="btn btn-sm btn-danger"
                                title="Eliminar"
                              >
                                <FaTrash />
                              </Link>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="9" className="text-center py-4">
                        No se encontraron asientos contables
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

export default AsientoList;