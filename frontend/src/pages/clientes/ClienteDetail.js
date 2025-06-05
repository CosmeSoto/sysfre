import React, { useState, useEffect } from 'react';
import { Container, Card, Row, Col, Button, Badge, Tab, Tabs, Table } from 'react-bootstrap';
import { useParams, Link } from 'react-router-dom';
import { FaEdit, FaTrash, FaPlus, FaMapMarkerAlt, FaPhone, FaEnvelope, FaIdCard } from 'react-icons/fa';
import { clientesService, ventasService } from '../../services/api';

const ClienteDetail = () => {
  const { id } = useParams();
  const [cliente, setCliente] = useState(null);
  const [direcciones, setDirecciones] = useState([]);
  const [ventas, setVentas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchClienteData = async () => {
      try {
        setLoading(true);
        
        // Cargar datos del cliente
        const clienteResponse = await clientesService.getCliente(id);
        setCliente(clienteResponse.data);
        
        // Cargar direcciones del cliente
        const direccionesResponse = await clientesService.getDirecciones({ cliente: id });
        setDirecciones(direccionesResponse.data.results);
        
        // Cargar ventas del cliente
        const ventasResponse = await ventasService.getVentas({ cliente: id });
        setVentas(ventasResponse.data.results);
      } catch (err) {
        setError('Error al cargar los datos del cliente');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchClienteData();
  }, [id]);

  if (loading) {
    return (
      <Container>
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Cargando...</span>
          </div>
          <p className="mt-3">Cargando datos del cliente...</p>
        </div>
      </Container>
    );
  }

  if (error || !cliente) {
    return (
      <Container>
        <div className="alert alert-danger" role="alert">
          {error || 'No se encontró el cliente'}
        </div>
        <Link to="/clientes" className="btn btn-primary">
          Volver a la lista
        </Link>
      </Container>
    );
  }

  return (
    <Container fluid>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 className="h3">
          {cliente.nombres} {cliente.apellidos}
        </h1>
        <div>
          <Link to={`/clientes/${id}/editar`} className="btn btn-warning me-2">
            <FaEdit className="me-2" /> Editar
          </Link>
          <Link to="/clientes" className="btn btn-secondary">
            Volver
          </Link>
        </div>
      </div>
      
      <Row>
        <Col lg={4} className="mb-4">
          <Card>
            <Card.Header>
              <h5 className="card-title mb-0">Información del Cliente</h5>
            </Card.Header>
            <Card.Body>
              <div className="mb-3">
                <Badge bg="secondary" className="me-1">
                  {cliente.tipo_identificacion}
                </Badge>
                <span className="fw-bold">{cliente.identificacion}</span>
              </div>
              
              <div className="mb-3">
                <div className="d-flex align-items-center mb-2">
                  <FaIdCard className="me-2 text-primary" />
                  <span className="fw-bold">Nombre Completo</span>
                </div>
                <p>{cliente.nombres} {cliente.apellidos}</p>
              </div>
              
              <div className="mb-3">
                <div className="d-flex align-items-center mb-2">
                  <FaEnvelope className="me-2 text-primary" />
                  <span className="fw-bold">Email</span>
                </div>
                <p>{cliente.email}</p>
              </div>
              
              <div className="mb-3">
                <div className="d-flex align-items-center mb-2">
                  <FaPhone className="me-2 text-primary" />
                  <span className="fw-bold">Teléfono</span>
                </div>
                <p>{cliente.telefono}</p>
              </div>
              
              <div className="mb-3">
                <div className="d-flex align-items-center mb-2">
                  <FaMapMarkerAlt className="me-2 text-primary" />
                  <span className="fw-bold">Dirección Principal</span>
                </div>
                <p>
                  {cliente.direccion}<br />
                  {cliente.ciudad}, {cliente.provincia}
                </p>
              </div>
              
              {cliente.notas && (
                <div>
                  <div className="fw-bold mb-2">Notas</div>
                  <p>{cliente.notas}</p>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
        
        <Col lg={8}>
          <Tabs defaultActiveKey="direcciones" className="mb-4">
            <Tab eventKey="direcciones" title="Direcciones">
              <Card>
                <Card.Header className="d-flex justify-content-between align-items-center">
                  <h5 className="card-title mb-0">Direcciones</h5>
                  <Button variant="primary" size="sm" as={Link} to={`/clientes/${id}/direcciones/nueva`}>
                    <FaPlus className="me-1" /> Agregar Dirección
                  </Button>
                </Card.Header>
                <Card.Body>
                  {direcciones.length > 0 ? (
                    <div className="table-responsive">
                      <Table striped hover>
                        <thead>
                          <tr>
                            <th>Tipo</th>
                            <th>Nombre</th>
                            <th>Dirección</th>
                            <th>Ciudad</th>
                            <th>Principal</th>
                            <th>Acciones</th>
                          </tr>
                        </thead>
                        <tbody>
                          {direcciones.map(direccion => (
                            <tr key={direccion.id}>
                              <td>
                                <Badge bg="info">
                                  {direccion.tipo === 'facturacion' ? 'Facturación' : 'Envío'}
                                </Badge>
                              </td>
                              <td>{direccion.nombre}</td>
                              <td>{direccion.direccion}</td>
                              <td>{direccion.ciudad}</td>
                              <td>
                                {direccion.es_principal && (
                                  <Badge bg="success">Principal</Badge>
                                )}
                              </td>
                              <td>
                                <div className="btn-group">
                                  <Button 
                                    as={Link}
                                    to={`/clientes/${id}/direcciones/${direccion.id}/editar`}
                                    variant="warning"
                                    size="sm"
                                  >
                                    <FaEdit />
                                  </Button>
                                  <Button 
                                    as={Link}
                                    to={`/clientes/${id}/direcciones/${direccion.id}/eliminar`}
                                    variant="danger"
                                    size="sm"
                                  >
                                    <FaTrash />
                                  </Button>
                                </div>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </Table>
                    </div>
                  ) : (
                    <div className="text-center py-4">
                      <p>No hay direcciones registradas</p>
                      <Button 
                        variant="primary" 
                        as={Link} 
                        to={`/clientes/${id}/direcciones/nueva`}
                      >
                        Agregar Dirección
                      </Button>
                    </div>
                  )}
                </Card.Body>
              </Card>
            </Tab>
            
            <Tab eventKey="ventas" title="Ventas">
              <Card>
                <Card.Header className="d-flex justify-content-between align-items-center">
                  <h5 className="card-title mb-0">Historial de Ventas</h5>
                  <Button variant="primary" size="sm" as={Link} to={`/ventas/nueva?cliente=${id}`}>
                    <FaPlus className="me-1" /> Nueva Venta
                  </Button>
                </Card.Header>
                <Card.Body>
                  {ventas.length > 0 ? (
                    <div className="table-responsive">
                      <Table striped hover>
                        <thead>
                          <tr>
                            <th>Número</th>
                            <th>Fecha</th>
                            <th>Tipo</th>
                            <th>Total</th>
                            <th>Estado</th>
                            <th>Acciones</th>
                          </tr>
                        </thead>
                        <tbody>
                          {ventas.map(venta => (
                            <tr key={venta.id}>
                              <td>{venta.numero}</td>
                              <td>{new Date(venta.fecha).toLocaleDateString()}</td>
                              <td>
                                <Badge bg="info">
                                  {venta.tipo === 'factura' ? 'Factura' : 'Nota de Venta'}
                                </Badge>
                              </td>
                              <td>${venta.total.toFixed(2)}</td>
                              <td>
                                <Badge bg={
                                  venta.estado === 'pagado' ? 'success' :
                                  venta.estado === 'pendiente' ? 'warning' :
                                  venta.estado === 'anulado' ? 'danger' : 'secondary'
                                }>
                                  {venta.estado}
                                </Badge>
                              </td>
                              <td>
                                <Link 
                                  to={`/ventas/${venta.id}`}
                                  className="btn btn-sm btn-info"
                                >
                                  Ver
                                </Link>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </Table>
                    </div>
                  ) : (
                    <div className="text-center py-4">
                      <p>No hay ventas registradas</p>
                      <Button 
                        variant="primary" 
                        as={Link} 
                        to={`/ventas/nueva?cliente=${id}`}
                      >
                        Crear Venta
                      </Button>
                    </div>
                  )}
                </Card.Body>
              </Card>
            </Tab>
          </Tabs>
        </Col>
      </Row>
    </Container>
  );
};

export default ClienteDetail;