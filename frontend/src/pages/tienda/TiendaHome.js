import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Form, Badge } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { FaSearch, FaShoppingCart, FaStar } from 'react-icons/fa';
import { tiendaService } from '../../services/api';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import ErrorMessage from '../../components/common/ErrorMessage';
import { formatCurrency } from '../../utils/formatters';

const TiendaHome = () => {
  const [productos, setProductos] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filtros, setFiltros] = useState({
    categoria: '',
    precioMin: '',
    precioMax: '',
    ordenar: 'nombre',
    busqueda: ''
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Cargar categorías
        const categoriasResponse = await tiendaService.getCategorias();
        setCategorias(categoriasResponse.data);
        
        // Cargar productos
        await fetchProductos();
      } catch (err) {
        setError('Error al cargar los datos de la tienda');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);

  const fetchProductos = async () => {
    try {
      setLoading(true);
      const params = { ...filtros };
      
      const response = await tiendaService.getProductos(params);
      setProductos(response.data.results);
    } catch (err) {
      setError('Error al cargar los productos');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleFiltroChange = (e) => {
    const { name, value } = e.target;
    setFiltros(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleBusqueda = (e) => {
    e.preventDefault();
    fetchProductos();
  };

  const handleAgregarAlCarrito = async (productoId) => {
    try {
      await tiendaService.agregarAlCarrito({ producto_id: productoId, cantidad: 1 });
      // Actualizar contador de carrito (implementar en un contexto global)
    } catch (err) {
      console.error('Error al agregar al carrito:', err);
    }
  };

  if (loading && productos.length === 0) {
    return <LoadingSpinner text="Cargando productos..." />;
  }

  return (
    <Container fluid>
      <div className="bg-light p-4 mb-4 rounded">
        <Row className="align-items-center">
          <Col md={8}>
            <h1 className="display-5">Bienvenido a nuestra Tienda Online</h1>
            <p className="lead">Descubre nuestros productos de alta calidad a precios increíbles</p>
          </Col>
          <Col md={4}>
            <Form onSubmit={handleBusqueda}>
              <div className="input-group">
                <Form.Control
                  type="text"
                  placeholder="Buscar productos..."
                  name="busqueda"
                  value={filtros.busqueda}
                  onChange={handleFiltroChange}
                />
                <Button type="submit" variant="primary">
                  <FaSearch />
                </Button>
              </div>
            </Form>
          </Col>
        </Row>
      </div>

      <ErrorMessage error={error} />

      <Row>
        <Col lg={3} className="mb-4">
          <Card>
            <Card.Header>
              <h5 className="mb-0">Filtros</h5>
            </Card.Header>
            <Card.Body>
              <Form>
                <Form.Group className="mb-3">
                  <Form.Label>Categoría</Form.Label>
                  <Form.Select
                    name="categoria"
                    value={filtros.categoria}
                    onChange={handleFiltroChange}
                  >
                    <option value="">Todas las categorías</option>
                    {categorias.map(categoria => (
                      <option key={categoria.id} value={categoria.id}>
                        {categoria.nombre}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Precio</Form.Label>
                  <Row>
                    <Col>
                      <Form.Control
                        type="number"
                        placeholder="Min"
                        name="precioMin"
                        value={filtros.precioMin}
                        onChange={handleFiltroChange}
                      />
                    </Col>
                    <Col>
                      <Form.Control
                        type="number"
                        placeholder="Max"
                        name="precioMax"
                        value={filtros.precioMax}
                        onChange={handleFiltroChange}
                      />
                    </Col>
                  </Row>
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Ordenar por</Form.Label>
                  <Form.Select
                    name="ordenar"
                    value={filtros.ordenar}
                    onChange={handleFiltroChange}
                  >
                    <option value="nombre">Nombre (A-Z)</option>
                    <option value="-nombre">Nombre (Z-A)</option>
                    <option value="precio">Precio (menor a mayor)</option>
                    <option value="-precio">Precio (mayor a menor)</option>
                    <option value="-creado">Más recientes</option>
                  </Form.Select>
                </Form.Group>

                <div className="d-grid">
                  <Button 
                    variant="primary" 
                    onClick={fetchProductos}
                  >
                    Aplicar Filtros
                  </Button>
                </div>
              </Form>
            </Card.Body>
          </Card>

          <Card className="mt-4">
            <Card.Header>
              <h5 className="mb-0">Categorías Populares</h5>
            </Card.Header>
            <Card.Body>
              <div className="d-grid gap-2">
                {categorias.slice(0, 5).map(categoria => (
                  <Button 
                    key={categoria.id}
                    variant="outline-secondary"
                    onClick={() => {
                      setFiltros(prev => ({ ...prev, categoria: categoria.id }));
                      fetchProductos();
                    }}
                  >
                    {categoria.nombre}
                  </Button>
                ))}
              </div>
            </Card.Body>
          </Card>
        </Col>

        <Col lg={9}>
          {loading && productos.length > 0 ? (
            <div className="text-center py-3">
              <LoadingSpinner size="sm" centered={false} text="Actualizando..." />
            </div>
          ) : (
            <>
              <div className="d-flex justify-content-between align-items-center mb-4">
                <h2>Productos</h2>
                <span>{productos.length} productos encontrados</span>
              </div>

              <Row xs={1} md={2} lg={3} className="g-4">
                {productos.length > 0 ? (
                  productos.map(producto => (
                    <Col key={producto.id}>
                      <Card className="h-100 product-card">
                        <div className="product-image-container">
                          <Card.Img 
                            variant="top" 
                            src={producto.imagen || 'https://via.placeholder.com/300x200'} 
                            alt={producto.nombre}
                          />
                          {producto.descuento > 0 && (
                            <Badge 
                              bg="danger" 
                              className="position-absolute top-0 end-0 m-2"
                            >
                              -{producto.descuento}%
                            </Badge>
                          )}
                        </div>
                        <Card.Body>
                          <Card.Title>{producto.nombre}</Card.Title>
                          <div className="mb-2">
                            {[...Array(5)].map((_, i) => (
                              <FaStar 
                                key={i} 
                                className={i < producto.valoracion ? "text-warning" : "text-muted"}
                              />
                            ))}
                            <small className="ms-1 text-muted">({producto.num_valoraciones})</small>
                          </div>
                          <Card.Text className="text-truncate">
                            {producto.descripcion}
                          </Card.Text>
                          <div className="d-flex justify-content-between align-items-center">
                            <div>
                              {producto.precio_anterior && (
                                <span className="text-muted text-decoration-line-through me-2">
                                  {formatCurrency(producto.precio_anterior)}
                                </span>
                              )}
                              <span className="fw-bold fs-5">
                                {formatCurrency(producto.precio)}
                              </span>
                            </div>
                            <Badge bg={producto.stock > 0 ? "success" : "danger"}>
                              {producto.stock > 0 ? "En stock" : "Agotado"}
                            </Badge>
                          </div>
                        </Card.Body>
                        <Card.Footer className="bg-white border-top-0">
                          <div className="d-grid gap-2">
                            <Button 
                              variant="primary"
                              onClick={() => handleAgregarAlCarrito(producto.id)}
                              disabled={producto.stock <= 0}
                            >
                              <FaShoppingCart className="me-2" /> Agregar al carrito
                            </Button>
                            <Link 
                              to={`/tienda/productos/${producto.id}`}
                              className="btn btn-outline-secondary"
                            >
                              Ver detalles
                            </Link>
                          </div>
                        </Card.Footer>
                      </Card>
                    </Col>
                  ))
                ) : (
                  <Col xs={12}>
                    <div className="text-center py-5">
                      <h3>No se encontraron productos</h3>
                      <p>Intenta con otros filtros de búsqueda</p>
                    </div>
                  </Col>
                )}
              </Row>
            </>
          )}
        </Col>
      </Row>
    </Container>
  );
};

export default TiendaHome;