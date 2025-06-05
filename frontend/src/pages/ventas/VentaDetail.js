import React, { useState, useEffect } from 'react';
import { Container, Card, Row, Col, Button, Badge, Table, Alert } from 'react-bootstrap';
import { useParams, Link } from 'react-router-dom';
import { FaPrint, FaFileInvoice, FaMoneyBillWave, FaTimes, FaCheck } from 'react-icons/fa';
import { ventasService } from '../../services/api';
import { toast } from 'react-toastify';

const VentaDetail = () => {
  const { id } = useParams();
  const [venta, setVenta] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [processingAction, setProcessingAction] = useState(false);

  useEffect(() => {
    const fetchVenta = async () => {
      try {
        setLoading(true);
        const response = await ventasService.getVenta(id);
        setVenta(response.data);
      } catch (err) {
        setError('Error al cargar los datos de la venta');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchVenta();
  }, [id]);

  // Función para cambiar el estado de la venta
  const handleCambiarEstado = async (nuevoEstado) => {
    try {
      setProcessingAction(true);
      await ventasService.cambiarEstado(id, { estado: nuevoEstado });
      
      // Actualizar la venta en el estado
      const response = await ventasService.getVenta(id);
      setVenta(response.data);
      
      toast.success(`Estado cambiado a ${nuevoEstado} correctamente`);
    } catch (err) {
      toast.error('Error al cambiar el estado de la venta');
      console.error(err);
    } finally {
      setProcessingAction(false);
    }
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

  if (loading) {
    return (
      <Container>
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Cargando...</span>
          </div>
          <p className="mt-3">Cargando datos de la venta...</p>
        </div>
      </Container>
    );
  }

  if (error || !venta) {
    return (
      <Container>
        <Alert variant="danger">
          {error || 'No se encontró la venta'}
        </Alert>
        <Link to="/ventas" className="btn btn-primary">
          Volver a la lista
        </Link>
      </Container>
    );
  }

  return (
    <Container fluid>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 className="h3">
          {venta.tipo === 'factura' ? 'Factura' : 'Nota de Venta'}: {venta.numero}
        </h1>
        <div>
          <Link to={`/ventas/${id}/imprimir`} className="btn btn-secondary me-2">
            <FaPrint className="me-2" /> Imprimir
          </Link>
          <Link to={`/ventas/${id}/factura`} className="btn btn-primary me-2">
            <FaFileInvoice className="me-2" /> Ver Factura
          </Link>
          <Link to="/ventas" className="btn btn-outline-secondary">
            Volver
          </Link>
        </div>
      </div>
      
      <Row className="mb-4">
        <Col md={6}>
          <Card className="h-100">
            <Card.Header>
              <h5 className="card-title mb-0">Información de la Venta</h5>
            </Card.Header>
            <Card.Body>
              <Row className="mb-3">
                <Col sm={4} className="fw-bold">Número:</Col>
                <Col sm={8}>{venta.numero}</Col>
              </Row>
              <Row className="mb-3">
                <Col sm={4} className="fw-bold">Fecha:</Col>
                <Col sm={8}>{new Date(venta.fecha).toLocaleDateString()}</Col>
              </Row>
              <Row className="mb-3">
                <Col sm={4} className="fw-bold">Tipo:</Col>
                <Col sm={8}>
                  <Badge bg="info">
                    {venta.tipo === 'factura' ? 'Factura' : 'Nota de Venta'}
                  </Badge>
                </Col>
              </Row>
              <Row className="mb-3">
                <Col sm={4} className="fw-bold">Estado:</Col>
                <Col sm={8}>{renderEstado(venta.estado)}</Col>
              </Row>
              <Row className="mb-3">
                <Col sm={4} className="fw-bold">Cliente:</Col>
                <Col sm={8}>
                  <Link to={`/clientes/${venta.cliente}`}>
                    {venta.cliente_nombre}
                  </Link>
                </Col>
              </Row>
              {venta.notas && (
                <Row className="mb-3">
                  <Col sm={4} className="fw-bold">Notas:</Col>
                  <Col sm={8}>{venta.notas}</Col>
                </Row>
              )}
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={6}>
          <Card className="h-100">
            <Card.Header className="d-flex justify-content-between align-items-center">
              <h5 className="card-title mb-0">Acciones</h5>
              <div>
                {venta.estado === 'borrador' && (
                  <Button 
                    variant="success" 
                    className="me-2"
                    disabled={processingAction}
                    onClick={() => handleCambiarEstado('pendiente')}
                  >
                    <FaCheck className="me-2" /> Confirmar
                  </Button>
                )}
                
                {venta.estado === 'pendiente' && (
                  <Button 
                    variant="success" 
                    className="me-2"
                    disabled={processingAction}
                    as={Link}
                    to={`/ventas/${id}/pago`}
                  >
                    <FaMoneyBillWave className="me-2" /> Registrar Pago
                  </Button>
                )}
                
                {(venta.estado === 'borrador' || venta.estado === 'pendiente') && (
                  <Button 
                    variant="danger"
                    disabled={processingAction}
                    onClick={() => handleCambiarEstado('anulado')}
                  >
                    <FaTimes className="me-2" /> Anular
                  </Button>
                )}
              </div>
            </Card.Header>
            <Card.Body>
              <div className="d-flex justify-content-between mb-3">
                <span className="fw-bold">Subtotal:</span>
                <span>${venta.subtotal.toFixed(2)}</span>
              </div>
              
              {venta.descuento > 0 && (
                <div className="d-flex justify-content-between mb-3">
                  <span className="fw-bold">Descuento:</span>
                  <span>-${venta.descuento.toFixed(2)}</span>
                </div>
              )}
              
              <div className="d-flex justify-content-between mb-3">
                <span className="fw-bold">IVA ({venta.iva_porcentaje}%):</span>
                <span>${venta.iva.toFixed(2)}</span>
              </div>
              
              <div className="d-flex justify-content-between mb-3">
                <span className="fw-bold fs-5">Total:</span>
                <span className="fw-bold fs-5">${venta.total.toFixed(2)}</span>
              </div>
              
              <hr />
              
              {venta.pagos && venta.pagos.length > 0 ? (
                <>
                  <h6 className="mb-3">Pagos Registrados</h6>
                  <Table size="sm">
                    <thead>
                      <tr>
                        <th>Fecha</th>
                        <th>Método</th>
                        <th>Monto</th>
                        <th>Referencia</th>
                      </tr>
                    </thead>
                    <tbody>
                      {venta.pagos.map(pago => (
                        <tr key={pago.id}>
                          <td>{new Date(pago.fecha).toLocaleDateString()}</td>
                          <td>{pago.metodo}</td>
                          <td>${pago.monto.toFixed(2)}</td>
                          <td>{pago.referencia}</td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                </>
              ) : (
                venta.estado === 'pendiente' && (
                  <div className="text-center py-3">
                    <p>No hay pagos registrados</p>
                    <Button 
                      variant="primary"
                      as={Link}
                      to={`/ventas/${id}/pago`}
                    >
                      <FaMoneyBillWave className="me-2" /> Registrar Pago
                    </Button>
                  </div>
                )
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
      
      <Card>
        <Card.Header>
          <h5 className="card-title mb-0">Detalles de la Venta</h5>
        </Card.Header>
        <Card.Body>
          <div className="table-responsive">
            <Table striped>
              <thead>
                <tr>
                  <th>Producto</th>
                  <th className="text-center">Cantidad</th>
                  <th className="text-end">Precio Unitario</th>
                  <th className="text-end">Descuento</th>
                  <th className="text-end">Subtotal</th>
                  <th className="text-end">IVA</th>
                  <th className="text-end">Total</th>
                </tr>
              </thead>
              <tbody>
                {venta.detalles.map(detalle => (
                  <tr key={detalle.id}>
                    <td>
                      <Link to={`/inventario/productos/${detalle.producto}`}>
                        {detalle.producto_nombre}
                      </Link>
                    </td>
                    <td className="text-center">{detalle.cantidad}</td>
                    <td className="text-end">${detalle.precio_unitario.toFixed(2)}</td>
                    <td className="text-end">
                      {detalle.descuento > 0 ? `$${detalle.descuento.toFixed(2)}` : '-'}
                    </td>
                    <td className="text-end">${detalle.subtotal.toFixed(2)}</td>
                    <td className="text-end">${detalle.iva.toFixed(2)}</td>
                    <td className="text-end">${detalle.total.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr>
                  <th colSpan="4" className="text-end">Subtotal:</th>
                  <th className="text-end">${venta.subtotal.toFixed(2)}</th>
                  <th className="text-end">${venta.iva.toFixed(2)}</th>
                  <th className="text-end">${venta.total.toFixed(2)}</th>
                </tr>
              </tfoot>
            </Table>
          </div>
        </Card.Body>
      </Card>
    </Container>
  );
};

export default VentaDetail;