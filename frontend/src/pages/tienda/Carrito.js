import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Table, Form, Alert } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import { FaTrash, FaArrowLeft, FaShoppingCart, FaCreditCard } from 'react-icons/fa';
import { tiendaService } from '../../services/api';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import ErrorMessage from '../../components/common/ErrorMessage';
import { formatCurrency } from '../../utils/formatters';
import { toast } from 'react-toastify';

const Carrito = () => {
  const navigate = useNavigate();
  const [carrito, setCarrito] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actualizando, setActualizando] = useState(false);
  const [cuponCodigo, setCuponCodigo] = useState('');
  const [aplicandoCupon, setAplicandoCupon] = useState(false);

  useEffect(() => {
    fetchCarrito();
  }, []);

  const fetchCarrito = async () => {
    try {
      setLoading(true);
      const response = await tiendaService.getCarrito();
      setCarrito(response.data);
    } catch (err) {
      setError('Error al cargar el carrito');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCantidadChange = async (itemId, cantidad) => {
    if (cantidad < 1) return;
    
    try {
      setActualizando(true);
      await tiendaService.actualizarCantidadCarrito(itemId, { cantidad });
      await fetchCarrito();
    } catch (err) {
      toast.error('Error al actualizar la cantidad');
      console.error(err);
    } finally {
      setActualizando(false);
    }
  };

  const handleEliminarItem = async (itemId) => {
    try {
      setActualizando(true);
      await tiendaService.eliminarItemCarrito(itemId);
      await fetchCarrito();
      toast.success('Producto eliminado del carrito');
    } catch (err) {
      toast.error('Error al eliminar el producto');
      console.error(err);
    } finally {
      setActualizando(false);
    }
  };

  const handleVaciarCarrito = async () => {
    if (!window.confirm('¿Está seguro de vaciar el carrito?')) return;
    
    try {
      setActualizando(true);
      await tiendaService.vaciarCarrito();
      await fetchCarrito();
      toast.success('Carrito vaciado correctamente');
    } catch (err) {
      toast.error('Error al vaciar el carrito');
      console.error(err);
    } finally {
      setActualizando(false);
    }
  };

  const handleAplicarCupon = async (e) => {
    e.preventDefault();
    
    if (!cuponCodigo.trim()) {
      toast.error('Ingrese un código de cupón');
      return;
    }
    
    try {
      setAplicandoCupon(true);
      await tiendaService.aplicarCupon({ codigo: cuponCodigo });
      await fetchCarrito();
      toast.success('Cupón aplicado correctamente');
      setCuponCodigo('');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Error al aplicar el cupón');
      console.error(err);
    } finally {
      setAplicandoCupon(false);
    }
  };

  const handleProcederPago = () => {
    navigate('/tienda/checkout');
  };

  if (loading) {
    return <LoadingSpinner text="Cargando carrito..." />;
  }

  if (error) {
    return (
      <Container>
        <ErrorMessage error={error} />
        <Link to="/tienda" className="btn btn-primary">
          Volver a la tienda
        </Link>
      </Container>
    );
  }

  if (!carrito || carrito.items.length === 0) {
    return (
      <Container>
        <div className="text-center py-5">
          <FaShoppingCart size={64} className="text-muted mb-4" />
          <h2>Tu carrito está vacío</h2>
          <p className="mb-4">Parece que aún no has agregado productos a tu carrito.</p>
          <Link to="/tienda" className="btn btn-primary">
            <FaArrowLeft className="me-2" /> Ir a la tienda
          </Link>
        </div>
      </Container>
    );
  }

  return (
    <Container>
      <h1 className="mb-4">Tu Carrito</h1>
      
      {actualizando && (
        <Alert variant="info">
          Actualizando carrito...
        </Alert>
      )}
      
      <Row>
        <Col lg={8}>
          <Card className="mb-4">
            <Card.Body>
              <div className="table-responsive">
                <Table>
                  <thead>
                    <tr>
                      <th>Producto</th>
                      <th>Precio</th>
                      <th>Cantidad</th>
                      <th>Subtotal</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {carrito.items.map(item => (
                      <tr key={item.id}>
                        <td>
                          <div className="d-flex align-items-center">
                            <img 
                              src={item.producto.imagen || 'https://via.placeholder.com/50'} 
                              alt={item.producto.nombre}
                              style={{ width: '50px', height: '50px', objectFit: 'cover' }}
                              className="me-3"
                            />
                            <div>
                              <Link to={`/tienda/productos/${item.producto.id}`} className="text-decoration-none">
                                {item.producto.nombre}
                              </Link>
                              {item.producto.stock < item.cantidad && (
                                <div className="text-danger small">
                                  ¡Solo {item.producto.stock} disponibles!
                                </div>
                              )}
                            </div>
                          </div>
                        </td>
                        <td>{formatCurrency(item.precio_unitario)}</td>
                        <td style={{ width: '120px' }}>
                          <div className="d-flex align-items-center">
                            <Button 
                              variant="outline-secondary" 
                              size="sm"
                              onClick={() => handleCantidadChange(item.id, item.cantidad - 1)}
                              disabled={item.cantidad <= 1 || actualizando}
                            >
                              -
                            </Button>
                            <Form.Control
                              type="number"
                              min="1"
                              value={item.cantidad}
                              onChange={(e) => handleCantidadChange(item.id, parseInt(e.target.value))}
                              disabled={actualizando}
                              className="mx-2 text-center"
                              style={{ width: '60px' }}
                            />
                            <Button 
                              variant="outline-secondary" 
                              size="sm"
                              onClick={() => handleCantidadChange(item.id, item.cantidad + 1)}
                              disabled={item.cantidad >= item.producto.stock || actualizando}
                            >
                              +
                            </Button>
                          </div>
                        </td>
                        <td>{formatCurrency(item.subtotal)}</td>
                        <td>
                          <Button 
                            variant="outline-danger" 
                            size="sm"
                            onClick={() => handleEliminarItem(item.id)}
                            disabled={actualizando}
                          >
                            <FaTrash />
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </div>
              
              <div className="d-flex justify-content-between mt-3">
                <Button 
                  variant="outline-secondary"
                  as={Link}
                  to="/tienda"
                >
                  <FaArrowLeft className="me-2" /> Seguir comprando
                </Button>
                <Button 
                  variant="outline-danger"
                  onClick={handleVaciarCarrito}
                  disabled={actualizando}
                >
                  <FaTrash className="me-2" /> Vaciar carrito
                </Button>
              </div>
            </Card.Body>
          </Card>
        </Col>
        
        <Col lg={4}>
          <Card className="mb-4">
            <Card.Header>
              <h5 className="mb-0">Resumen del pedido</h5>
            </Card.Header>
            <Card.Body>
              <div className="d-flex justify-content-between mb-2">
                <span>Subtotal</span>
                <span>{formatCurrency(carrito.subtotal)}</span>
              </div>
              
              {carrito.descuento > 0 && (
                <div className="d-flex justify-content-between mb-2 text-success">
                  <span>Descuento</span>
                  <span>-{formatCurrency(carrito.descuento)}</span>
                </div>
              )}
              
              <div className="d-flex justify-content-between mb-2">
                <span>IVA ({carrito.iva_porcentaje}%)</span>
                <span>{formatCurrency(carrito.iva)}</span>
              </div>
              
              <hr />
              
              <div className="d-flex justify-content-between mb-4">
                <span className="fw-bold">Total</span>
                <span className="fw-bold fs-5">{formatCurrency(carrito.total)}</span>
              </div>
              
              <div className="d-grid">
                <Button 
                  variant="primary" 
                  size="lg"
                  onClick={handleProcederPago}
                  disabled={actualizando}
                >
                  <FaCreditCard className="me-2" /> Proceder al pago
                </Button>
              </div>
            </Card.Body>
          </Card>
          
          <Card>
            <Card.Header>
              <h5 className="mb-0">Cupón de descuento</h5>
            </Card.Header>
            <Card.Body>
              <Form onSubmit={handleAplicarCupon}>
                <div className="d-flex">
                  <Form.Control
                    type="text"
                    placeholder="Código de cupón"
                    value={cuponCodigo}
                    onChange={(e) => setCuponCodigo(e.target.value)}
                    disabled={aplicandoCupon}
                    className="me-2"
                  />
                  <Button 
                    type="submit" 
                    variant="outline-primary"
                    disabled={aplicandoCupon || !cuponCodigo.trim()}
                  >
                    Aplicar
                  </Button>
                </div>
              </Form>
              
              {carrito.cupon && (
                <div className="mt-3 p-2 bg-light rounded">
                  <div className="d-flex justify-content-between align-items-center">
                    <div>
                      <span className="badge bg-success me-2">{carrito.cupon.codigo}</span>
                      <small>{carrito.cupon.descripcion}</small>
                    </div>
                    <Button 
                      variant="link" 
                      className="text-danger p-0"
                      onClick={async () => {
                        try {
                          await tiendaService.eliminarCupon();
                          await fetchCarrito();
                          toast.success('Cupón eliminado');
                        } catch (err) {
                          toast.error('Error al eliminar el cupón');
                        }
                      }}
                    >
                      Eliminar
                    </Button>
                  </div>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Carrito;