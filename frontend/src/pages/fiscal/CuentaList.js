import React, { useState, useEffect } from 'react';
import { Container, Card, Row, Col, Table, Badge, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { FaPlus, FaEdit, FaTrash, FaEye } from 'react-icons/fa';
import { fiscalService } from '../../services/api';
import SearchBar from '../../components/common/SearchBar';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import ErrorMessage from '../../components/common/ErrorMessage';
import { formatCurrency } from '../../utils/formatters';

const CuentaList = () => {
  const [cuentas, setCuentas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    tipo: '',
    search: ''
  });

  useEffect(() => {
    fetchCuentas();
  }, [filters]);

  const fetchCuentas = async () => {
    try {
      setLoading(true);
      const params = { ...filters };
      
      const response = await fiscalService.getCuentas(params);
      setCuentas(response.data);
    } catch (err) {
      setError('Error al cargar el plan de cuentas');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (searchTerm) => {
    setFilters(prev => ({ ...prev, search: searchTerm }));
  };

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  const renderTipoCuenta = (tipo) => {
    switch (tipo) {
      case 'activo':
        return <Badge bg="primary">Activo</Badge>;
      case 'pasivo':
        return <Badge bg="danger">Pasivo</Badge>;
      case 'patrimonio':
        return <Badge bg="success">Patrimonio</Badge>;
      case 'ingreso':
        return <Badge bg="info">Ingreso</Badge>;
      case 'gasto':
        return <Badge bg="warning">Gasto</Badge>;
      default:
        return <Badge bg="secondary">{tipo}</Badge>;
    }
  };

  // Función para renderizar cuentas de forma jerárquica
  const renderCuentas = (cuentas, nivel = 0) => {
    return cuentas.map(cuenta => (
      <React.Fragment key={cuenta.id}>
        <tr>
          <td>
            <div style={{ paddingLeft: `${nivel * 20}px` }}>
              {cuenta.codigo}
            </div>
          </td>
          <td>
            <div style={{ paddingLeft: `${nivel * 20}px` }}>
              {cuenta.nombre}
            </div>
          </td>
          <td>{renderTipoCuenta(cuenta.tipo)}</td>
          <td>{formatCurrency(cuenta.saldo)}</td>
          <td>
            <div className="btn-group">
              <Link 
                to={`/fiscal/cuentas/${cuenta.id}`}
                className="btn btn-sm btn-info"
                title="Ver detalles"
              >
                <FaEye />
              </Link>
              <Link 
                to={`/fiscal/cuentas/${cuenta.id}/editar`}
                className="btn btn-sm btn-warning"
                title="Editar"
              >
                <FaEdit />
              </Link>
              {!cuenta.subcuentas?.length && (
                <Link 
                  to={`/fiscal/cuentas/${cuenta.id}/eliminar`}
                  className="btn btn-sm btn-danger"
                  title="Eliminar"
                >
                  <FaTrash />
                </Link>
              )}
            </div>
          </td>
        </tr>
        {cuenta.subcuentas && cuenta.subcuentas.length > 0 && 
          renderCuentas(cuenta.subcuentas, nivel + 1)}
      </React.Fragment>
    ));
  };

  if (loading && cuentas.length === 0) {
    return <LoadingSpinner text="Cargando plan de cuentas..." />;
  }

  return (
    <Container fluid>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 className="h3">Plan de Cuentas</h1>
        <Link to="/fiscal/cuentas/nueva" className="btn btn-primary">
          <FaPlus className="me-2" /> Nueva Cuenta
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
                placeholder="Buscar por código o nombre"
                buttonText="Buscar"
              />
            </Col>
            <Col md={4}>
              <label className="form-label">Tipo de Cuenta</label>
              <select 
                className="form-select" 
                name="tipo" 
                value={filters.tipo} 
                onChange={handleFilterChange}
              >
                <option value="">Todos</option>
                <option value="activo">Activo</option>
                <option value="pasivo">Pasivo</option>
                <option value="patrimonio">Patrimonio</option>
                <option value="ingreso">Ingreso</option>
                <option value="gasto">Gasto</option>
              </select>
            </Col>
          </Row>
        </Card.Body>
      </Card>

      <Card>
        <Card.Body>
          {loading && cuentas.length > 0 ? (
            <div className="text-center py-3">
              <LoadingSpinner size="sm" centered={false} text="Actualizando..." />
            </div>
          ) : (
            <div className="table-responsive">
              <Table striped hover>
                <thead>
                  <tr>
                    <th>Código</th>
                    <th>Nombre</th>
                    <th>Tipo</th>
                    <th>Saldo</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {cuentas.length > 0 ? (
                    renderCuentas(cuentas)
                  ) : (
                    <tr>
                      <td colSpan="5" className="text-center py-4">
                        No se encontraron cuentas contables
                      </td>
                    </tr>
                  )}
                </tbody>
              </Table>
            </div>
          )}
        </Card.Body>
      </Card>
    </Container>
  );
};

export default CuentaList;