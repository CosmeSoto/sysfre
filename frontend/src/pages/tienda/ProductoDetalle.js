import { Table } from 'react-bootstrap';
import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Form, Badge, Tabs, Tab, ListGroup } from 'react-bootstrap';
import { useParams, Link } from 'react-router-dom';
import { FaShoppingCart, FaStar, FaHeart, FaShare, FaCheck } from 'react-icons/fa';
import { tiendaService } from '../../services/api';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import ErrorMessage from '../../components/common/ErrorMessage';
import { formatCurrency, formatDate } from '../../utils/formatters';
import { toast } from 'react-toastify';

const ProductoDetalle = () => {
  const { id } = useParams();
  const [producto, setProducto] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [cantidad, setCantidad] = useState(1);
  const [productosRelacionados, setProductosRelacionados] = useState([]);
  const [valoracion, setValoracion] = useState(0);
  const [comentario, setComentario] = useState('');

  useEffect(() => {
    const fetchProducto = async () => {
      try {
        setLoading(true);
        
        // Cargar producto
        const response = await tiendaService.getProducto(id);
        setProducto(response.data);
        
        // Cargar productos relacionados
        const relacionadosResponse = await tiendaService.getProductosRelacionados(id);
        setProductosRelacionados(relacionadosResponse.data);
      } catch (err) {
        setError('Error al cargar los datos del producto');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchProducto();
  }, [id]);

  const handleCantidadChange = (e) => {
    const value = parseInt(e.target.value);
    if (value > 0 && value <= (producto?.stock || 1)) {
      setCantidad(value);
    }
  };

  const handleAgregarAlCarrito = async () => {
    try {
      await tiendaService.agregarAlCarrito({ 
        producto_id: producto.id, 
        cantidad 
      });
      toast.success(`${producto.nombre} agregado al carrito`);
    } catch (err) {
      toast.error('Error al agregar al carrito');
      console.error(err);
    }
  };

  const handleAgregarAFavoritos = async () => {
    try {
      await tiendaService.agregarAFavoritos(producto.id);
      toast.success(`${producto.nombre} agregado a favoritos`);
    } catch (err) {
      toast.error('Error al agregar a favoritos');
      console.error(err);
    }
  };

  const handleEnviarValoracion = async (e) => {
    e.preventDefault();
    
    if (valoracion === 0) {
      toast.error('Debe seleccionar una valoración');
      return;
    }
    
    try {
      await tiendaService.valorarProducto(producto.id, {
        valoracion,
        comentario
      });
      toast.success('Valoración enviada correctamente');
      
      // Recargar producto para actualizar valoraciones
      const response = await tiendaService.getProducto(id);
      setProducto(response.data);
      
      // Limpiar formulario
      setValoracion(0);
      setComentario('');
    } catch (err) {
      toast.error('Error al enviar la valoración');
      console.error(err);
    }
  };

  if (loading) {
    return <LoadingSpinner text="Cargando producto..." />;
  }

  if (error || !producto) {
    return (
      <Container>
        <ErrorMessage error={error || 'No se encontró el producto'} />
        <Link to="/tienda" className="btn btn-primary">
          Volver a la tienda
        </Link>
      </Container>
    );
  }

  return (
    <Container>
      <nav aria-label="breadcrumb" className="mb-4">
        <ol className="breadcrumb">
          <li className="breadcrumb-item"><Link to="/tienda">Tienda</Link></li>
          <li className="breadcrumb-item"><Link to={`/tienda/categorias/${producto.categoria.id}`}>{producto.categoria.nombre}</Link></li>
          <li className="breadcrumb-item active" aria-current="page">{producto.nombre}</li>
        </ol>
      </nav>

      <Row className="mb-5">
        <Col md={6} className="mb-4">
          <div className="product-image-container">
            <img 
              src={producto.imagen || 'https://via.placeholder.com/600x400'} 
              alt={producto.nombre}
              className="img-fluid rounded"
            />
            {producto.descuento > 0 && (
              <Badge 
                bg="danger" 
                className="position-absolute top-0 end-0 m-3 p-2"
              >
                -{producto.descuento}% DESCUENTO
              </Badge>
            )}
          </div>
          
          {producto.imagenes_adicionales && producto.imagenes_adicionales.length > 0 && (
            <Row className="mt-3">
              {producto.imagenes_adicionales.map((imagen, index) => (
                <Col key={index} xs={3}>
                  <img 
                    src={imagen} 
                    alt={`${producto.nombre} - Imagen ${index + 1}`}
                    className="img-fluid rounded cursor-pointer"
                  />
                </Col>
              ))}
            </Row>
          )}
        </Col>
        
        <Col md={6}>
          <h1 className="mb-2">{producto.nombre}</h1>
          
          <div className="mb-3 d-flex align-items-center">
            {[...Array(5)].map((_, i) => (
              <FaStar 
                key={i} 
                className={i < producto.valoracion ? "text-warning" : "text-muted"}
                size={20}
              />
            ))}
            <span className="ms-2">
              {producto.valoracion.toFixed(1)} ({producto.num_valoraciones} valoraciones)
            </span>
          </div>
          
          <div className="mb-4">
            {producto.precio_anterior && (
              <span className="text-muted text-decoration-line-through me-2 fs-5">
                {formatCurrency(producto.precio_anterior)}
              </span>
            )}
            <span className="fw-bold fs-2 text-primary">
              {formatCurrency(producto.precio)}
            </span>
            
            <Badge 
              bg={producto.stock > 10 ? "success" : (producto.stock > 0 ? "warning" : "danger")}
              className="ms-3"
            >
              {producto.stock > 10 ? "En stock" : (producto.stock > 0 ? `¡Solo quedan ${producto.stock}!` : "Agotado")}
            </Badge>
          </div>
          
          <p className="mb-4">{producto.descripcion_corta}</p>
          
          <div className="mb-4">
            <Row>
              <Col md={4}>
                <Form.Group>
                  <Form.Label>Cantidad</Form.Label>
                  <Form.Control
                    type="number"
                    min="1"
                    max={producto.stock}
                    value={cantidad}
                    onChange={handleCantidadChange}
                    disabled={producto.stock <= 0}
                  />
                </Form.Group>
              </Col>
            </Row>
          </div>
          
          <div className="d-grid gap-2 mb-4">
            <Button 
              variant="primary" 
              size="lg"
              onClick={handleAgregarAlCarrito}
              disabled={producto.stock <= 0}
            >
              <FaShoppingCart className="me-2" /> Agregar al carrito
            </Button>
            
            <div className="d-flex gap-2">
              <Button 
                variant="outline-danger" 
                className="flex-grow-1"
                onClick={handleAgregarAFavoritos}
              >
                <FaHeart className="me-2" /> Agregar a favoritos
              </Button>
              <Button 
                variant="outline-secondary"
                className="flex-grow-1"
              >
                <FaShare className="me-2" /> Compartir
              </Button>
            </div>
          </div>
          
          <div className="mb-4">
            <h5>Características:</h5>
            <ListGroup variant="flush">
              {producto.caracteristicas && producto.caracteristicas.map((caracteristica, index) => (
                <ListGroup.Item key={index} className="d-flex align-items-center">
                  <FaCheck className="text-success me-2" /> {caracteristica}
                </ListGroup.Item>
              ))}
            </ListGroup>
          </div>
          
          <div>
            <p className="mb-1"><strong>SKU:</strong> {producto.codigo}</p>
            <p className="mb-1"><strong>Categoría:</strong> {producto.categoria.nombre}</p>
            <p className="mb-0"><strong>Marca:</strong> {producto.marca}</p>
          </div>
        </Col>
      </Row>
      
      <Tabs defaultActiveKey="descripcion" className="mb-4">
        <Tab eventKey="descripcion" title="Descripción">
          <Card.Body>
            <div dangerouslySetInnerHTML={{ __html: producto.descripcion_completa || producto.descripcion }} />
          </Card.Body>
        </Tab>
        <Tab eventKey="especificaciones" title="Especificaciones">
          <Card.Body>
            <Table striped bordered>
              <tbody>
                {producto.especificaciones && Object.entries(producto.especificaciones).map(([key, value]) => (
                  <tr key={key}>
                    <th>{key}</th>
                    <td>{value}</td>
                  </tr>
                ))}
              </tbody>
            </Table>
          </Card.Body>
        </Tab>
        <Tab eventKey="valoraciones" title={`Valoraciones (${producto.num_valoraciones})`}>
          <Card.Body>
            <h4 className="mb-4">Valoraciones de clientes</h4>
            
            {producto.valoraciones && producto.valoraciones.length > 0 ? (
              producto.valoraciones.map((valoracion, index) => (
                <Card key={index} className="mb-3">
                  <Card.Body>
                    <div className="d-flex justify-content-between mb-2">
                      <div>
                        <h5 className="mb-0">{valoracion.usuario_nombre}</h5>
                        <div>
                          {[...Array(5)].map((_, i) => (
                            <FaStar 
                              key={i} 
                              className={i < valoracion.valoracion ? "text-warning" : "text-muted"}
                            />
                          ))}
                        </div>
                      </div>
                      <small className="text-muted">{formatDate(valoracion.fecha)}</small>
                    </div>
                    <p className="mb-0">{valoracion.comentario}</p>
                  </Card.Body>
                </Card>
              ))
            ) : (
              <p>No hay valoraciones para este producto.</p>
            )}
            
            <hr className="my-4" />
            
            <h5>Deja tu valoración</h5>
            <Form onSubmit={handleEnviarValoracion}>
              <Form.Group className="mb-3">
                <Form.Label>Tu valoración</Form.Label>
                <div>
                  {[...Array(5)].map((_, i) => (
                    <FaStar 
                      key={i} 
                      className={i < valoracion ? "text-warning" : "text-muted"}
                      style={{ cursor: 'pointer', fontSize: '24px', marginRight: '5px' }}
                      onClick={() => setValoracion(i + 1)}
                    />
                  ))}
                </div>
              </Form.Group>
              
              <Form.Group className="mb-3">
                <Form.Label>Tu comentario</Form.Label>
                <Form.Control 
                  as="textarea" 
                  rows={4}
                  value={comentario}
                  onChange={(e) => setComentario(e.target.value)}
                  placeholder="Escribe tu opinión sobre este producto..."
                />
              </Form.Group>
              
              <Button type="submit" variant="primary">
                Enviar valoración
              </Button>
            </Form>
          </Card.Body>
        </Tab>
      </Tabs>
      
      {productosRelacionados.length > 0 && (
        <div className="mb-5">
          <h3 className="mb-4">Productos relacionados</h3>
          <Row xs={1} md={2} lg={4} className="g-4">
            {productosRelacionados.map(producto => (
              <Col key={producto.id}>
                <Card className="h-100 product-card">
                  <Card.Img 
                    variant="top" 
                    src={producto.imagen || 'https://via.placeholder.com/300x200'} 
                    alt={producto.nombre}
                  />
                  <Card.Body>
                    <Card.Title>{producto.nombre}</Card.Title>
                    <div className="mb-2">
                      {[...Array(5)].map((_, i) => (
                        <FaStar 
                          key={i} 
                          className={i < producto.valoracion ? "text-warning" : "text-muted"}
                          size={12}
                        />
                      ))}
                    </div>
                    <div className="d-flex justify-content-between align-items-center">
                      <span className="fw-bold">
                        {formatCurrency(producto.precio)}
                      </span>
                      <Link 
                        to={`/tienda/productos/${producto.id}`}
                        className="btn btn-sm btn-outline-primary"
                      >
                        Ver detalles
                      </Link>
                    </div>
                  </Card.Body>
                </Card>
              </Col>
            ))}
          </Row>
        </div>
      )}
    </Container>
  );
};

export default ProductoDetalle;