import React, { useState, useEffect } from 'react';
import { Container, Card, Row, Col, Badge, Button, Table, Form } from 'react-bootstrap';
import { useParams, Link } from 'react-router-dom';
import { FaEdit, FaTools, FaPrint, FaPlus, FaCheck, FaTimes } from 'react-icons/fa';
import { reparacionesService } from '../../services/api';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import ErrorMessage from '../../components/common/ErrorMessage';
import ConfirmDialog from '../../components/common/ConfirmDialog';
import { formatDate, formatCurrency } from '../../utils/formatters';
import { toast } from 'react-toastify';

const ReparacionDetail = () => {
  const { id } = useParams();
  const [reparacion, setReparacion] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [confirmAction, setConfirmAction] = useState(null);
  const [processingAction, setProcessingAction] = useState(false);
  const [nuevoEstado, setNuevoEstado] = useState('');

  useEffect(() => {
    fetchReparacion();
  }, [id]);

  const fetchReparacion = async () => {
    try {
      setLoading(true);
      const response = await reparacionesService.getReparacion(id);
      setReparacion(response.data);
    } catch (err) {
      setError('Error al cargar los datos de la reparación');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCambiarEstado = async () => {
    try {
      setProcessingAction(true);
      await reparacionesService.cambiarEstado(id, { estado: nuevoEstado });
      await fetchReparacion();
      toast.success(`Estado cambiado a ${nuevoEstado} correctamente`);
      setShowConfirmDialog(false);
    } catch (err) {
      toast.error('Error al cambiar el estado de la reparación');
      console.error(err);
    } finally {
      setProcessingAction(false);
    }
  };

  const prepararCambioEstado = (estado) => {
    setNuevoEstado(estado);
    setConfirmAction('cambiarEstado');
    setShowConfirmDialog(true);
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

  if (loading) {
    return <LoadingSpinner text="Cargando datos de la reparación..." />;
  }

  if (error || !reparacion) {
    return (
      <Container>
        <ErrorMessage error={error || 'No se encontró la reparación'} />
        <Link to="/reparaciones" className="btn btn-primary">
          Volver a la lista
        </Link>
      </Container>
    );
  }

  return (
    <Container fluid>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 className="h3">
          Orden de Reparación #{reparacion.numero_orden}
        </h1>
        <div>
          <Link to={`/reparaciones/${id}/editar`} className="btn btn-warning me-2">
            <FaEdit className="me-2" /> Editar
          </Link>
          <Link to={`/reparaciones/${id}/imprimir`} className="btn btn-secondary me-2">
            <FaPrint className="me-2" /> Imprimir
          </Link>
          <Link to="/reparaciones" className="btn btn-outline-secondary">
            Volver
          </Link>
        </div>
      </div>

      <Row>
        <Col lg={4} className="mb-4">
          <Card className="h-100">
            <Card.Header>
              <h5 className="card-title mb-0">Información del Cliente</h5>
            </Card.Header>
            <Card.Body>
              <h6>{reparacion.cliente.nombres} {reparacion.cliente.apellidos}</h6>
              <p className="mb-1">
                <strong>Identificación:</strong> {reparacion.cliente.identificacion}
              </p>
              <p className="mb-1">
                <strong>Teléfono:</strong> {reparacion.cliente.telefono}
              </p>
              <p className="mb-1">
                <strong>Email:</strong> {reparacion.cliente.email}
              </p>
              <p className="mb-0">
                <strong>Dirección:</strong> {reparacion.cliente.direccion}
              </p>
              
              <div className="mt-3">
                <Link to={`/clientes/${reparacion.cliente.id}`} className="btn btn-sm btn-outline-primary">
                  Ver Cliente
                </Link>
              </div>
            </Card.Body>
          </Card>
        </Col>
        
        <Col lg={4} className="mb-4">
          <Card className="h-100">
            <Card.Header>
              <h5 className="card-title mb-0">Información del Equipo</h5>
            </Card.Header>
            <Card.Body>
              <h6>{reparacion.equipo}</h6>
              <p className="mb-1">
                <strong>Marca:</strong> {reparacion.marca}
              </p>
              <p className="mb-1">
                <strong>Modelo:</strong> {reparacion.modelo}
              </p>
              <p className="mb-1">
                <strong>Número de Serie:</strong> {reparacion.numero_serie || 'N/A'}
              </p>
              <p className="mb-0">
                <strong>Problema Reportado:</strong> {reparacion.problema_reportado}
              </p>
            </Card.Body>
          </Card>
        </Col>
        
        <Col lg={4} className="mb-4">
          <Card className="h-100">
            <Card.Header className="d-flex justify-content-between align-items-center">
              <h5 className="card-title mb-0">Estado</h5>
              <div>{renderEstado(reparacion.estado)}</div>
            </Card.Header>
            <Card.Body>
              <p className="mb-1">
                <strong>Fecha de Recepción:</strong> {formatDate(reparacion.fecha_recepcion)}
              </p>
              <p className="mb-1">
                <strong>Fecha Estimada de Entrega:</strong> {formatDate(reparacion.fecha_entrega_estimada)}
              </p>
              {reparacion.fecha_entrega && (
                <p className="mb-1">
                  <strong>Fecha de Entrega:</strong> {formatDate(reparacion.fecha_entrega)}
                </p>
              )}
              <p className="mb-3">
                <strong>Técnico Asignado:</strong> {reparacion.tecnico_nombre || 'No asignado'}
              </p>
              
              <div className="mb-3">
                <label className="form-label">Cambiar Estado</label>
                <div className="d-grid gap-2">
                  {reparacion.estado === 'recibido' && (
                    <Button 
                      variant="primary" 
                      onClick={() => prepararCambioEstado('diagnostico')}
                    >
                      <FaTools className="me-2" /> Iniciar Diagnóstico
                    </Button>
                  )}
                  
                  {reparacion.estado === 'diagnostico' && (
                    <>
                      <Button 
                        variant="warning" 
                        onClick={() => prepararCambioEstado('reparacion')}
                      >
                        <FaTools className="me-2" /> Iniciar Reparación
                      </Button>
                      <Button 
                        variant="secondary" 
                        onClick={() => prepararCambioEstado('espera_repuestos')}
                      >
                        Espera de Repuestos
                      </Button>
                    </>
                  )}
                  
                  {(reparacion.estado === 'reparacion' || reparacion.estado === 'espera_repuestos') && (
                    <Button 
                      variant="success" 
                      onClick={() => prepararCambioEstado('terminado')}
                    >
                      <FaCheck className="me-2" /> Marcar como Terminado
                    </Button>
                  )}
                  
                  {reparacion.estado === 'terminado' && (
                    <Button 
                      variant="dark" 
                      onClick={() => prepararCambioEstado('entregado')}
                    >
                      Marcar como Entregado
                    </Button>
                  )}
                  
                  {reparacion.estado !== 'entregado' && reparacion.estado !== 'cancelado' && (
                    <Button 
                      variant="danger" 
                      onClick={() => prepararCambioEstado('cancelado')}
                    >
                      <FaTimes className="me-2" /> Cancelar Reparación
                    </Button>
                  )}
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
      
      <Row>
        <Col md={6} className="mb-4">
          <Card>
            <Card.Header className="d-flex justify-content-between align-items-center">
              <h5 className="card-title mb-0">Diagnóstico</h5>
              {reparacion.estado === 'diagnostico' && (
                <Link to={`/reparaciones/${id}/diagnostico`} className="btn btn-sm btn-primary">
                  <FaEdit className="me-2" /> Editar Diagnóstico
                </Link>
              )}
            </Card.Header>
            <Card.Body>
              {reparacion.diagnostico ? (
                <div>
                  <p>{reparacion.diagnostico}</p>
                  <p className="text-muted">
                    <small>Actualizado: {formatDate(reparacion.fecha_diagnostico)}</small>
                  </p>
                </div>
              ) : (
                <div className="text-center py-3">
                  <p className="text-muted">No hay diagnóstico registrado</p>
                  {reparacion.estado === 'diagnostico' && (
                    <Link to={`/reparaciones/${id}/diagnostico`} className="btn btn-primary">
                      Registrar Diagnóstico
                    </Link>
                  )}
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={6} className="mb-4">
          <Card>
            <Card.Header className="d-flex justify-content-between align-items-center">
              <h5 className="card-title mb-0">Solución</h5>
              {(reparacion.estado === 'reparacion' || reparacion.estado === 'terminado') && (
                <Link to={`/reparaciones/${id}/solucion`} className="btn btn-sm btn-primary">
                  <FaEdit className="me-2" /> Editar Solución
                </Link>
              )}
            </Card.Header>
            <Card.Body>
              {reparacion.solucion ? (
                <div>
                  <p>{reparacion.solucion}</p>
                  <p className="text-muted">
                    <small>Actualizado: {formatDate(reparacion.fecha_solucion)}</small>
                  </p>
                </div>
              ) : (
                <div className="text-center py-3">
                  <p className="text-muted">No hay solución registrada</p>
                  {reparacion.estado === 'reparacion' && (
                    <Link to={`/reparaciones/${id}/solucion`} className="btn btn-primary">
                      Registrar Solución
                    </Link>
                  )}
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
      
      <Card className="mb-4">
        <Card.Header className="d-flex justify-content-between align-items-center">
          <h5 className="card-title mb-0">Repuestos Utilizados</h5>
          {(reparacion.estado === 'reparacion' || reparacion.estado === 'espera_repuestos') && (
            <Link to={`/reparaciones/${id}/repuestos`} className="btn btn-sm btn-primary">
              <FaPlus className="me-2" /> Agregar Repuesto
            </Link>
          )}
        </Card.Header>
        <Card.Body>
          {reparacion.repuestos && reparacion.repuestos.length > 0 ? (
            <div className="table-responsive">
              <Table striped hover>
                <thead>
                  <tr>
                    <th>Producto</th>
                    <th>Cantidad</th>
                    <th>Precio Unitario</th>
                    <th>Subtotal</th>
                  </tr>
                </thead>
                <tbody>
                  {reparacion.repuestos.map((repuesto, index) => (
                    <tr key={index}>
                      <td>{repuesto.producto_nombre}</td>
                      <td>{repuesto.cantidad}</td>
                      <td>{formatCurrency(repuesto.precio_unitario)}</td>
                      <td>{formatCurrency(repuesto.subtotal)}</td>
                    </tr>
                  ))}
                </tbody>
                <tfoot>
                  <tr>
                    <th colSpan="3" className="text-end">Total Repuestos:</th>
                    <th>{formatCurrency(reparacion.total_repuestos)}</th>
                  </tr>
                </tfoot>
              </Table>
            </div>
          ) : (
            <div className="text-center py-3">
              <p className="text-muted">No hay repuestos registrados</p>
              {(reparacion.estado === 'reparacion' || reparacion.estado === 'espera_repuestos') && (
                <Link to={`/reparaciones/${id}/repuestos`} className="btn btn-primary">
                  Agregar Repuesto
                </Link>
              )}
            </div>
          )}
        </Card.Body>
      </Card>
      
      <Card>
        <Card.Header>
          <h5 className="card-title mb-0">Costos</h5>
        </Card.Header>
        <Card.Body>
          <Row>
            <Col md={6}>
              <div className="d-flex justify-content-between mb-2">
                <span>Costo de Diagnóstico:</span>
                <span>{formatCurrency(reparacion.costo_diagnostico)}</span>
              </div>
              <div className="d-flex justify-content-between mb-2">
                <span>Costo de Mano de Obra:</span>
                <span>{formatCurrency(reparacion.costo_mano_obra)}</span>
              </div>
              <div className="d-flex justify-content-between mb-2">
                <span>Costo de Repuestos:</span>
                <span>{formatCurrency(reparacion.total_repuestos)}</span>
              </div>
              <div className="d-flex justify-content-between mb-2">
                <span>Subtotal:</span>
                <span>{formatCurrency(reparacion.subtotal)}</span>
              </div>
              <div className="d-flex justify-content-between mb-2">
                <span>IVA ({reparacion.iva_porcentaje}%):</span>
                <span>{formatCurrency(reparacion.iva)}</span>
              </div>
              <div className="d-flex justify-content-between mb-2">
                <span className="fw-bold">Total:</span>
                <span className="fw-bold">{formatCurrency(reparacion.total)}</span>
              </div>
            </Col>
            <Col md={6}>
              <div className="card bg-light">
                <div className="card-body">
                  <h6>Notas Adicionales</h6>
                  <p className="mb-0">{reparacion.notas || 'Sin notas adicionales'}</p>
                </div>
              </div>
            </Col>
          </Row>
        </Card.Body>
      </Card>
      
      <ConfirmDialog
        show={showConfirmDialog}
        onHide={() => setShowConfirmDialog(false)}
        onConfirm={handleCambiarEstado}
        title="Confirmar Cambio de Estado"
        message={`¿Está seguro de cambiar el estado a "${nuevoEstado}"?`}
        confirmText="Cambiar Estado"
        isLoading={processingAction}
      />
    </Container>
  );
};

export default ReparacionDetail;