import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Form, Button, Table, Badge, Pagination } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { FaPlus, FaSearch, FaEye, FaEdit, FaTrash } from 'react-icons/fa';
import { inventarioService } from '../../services/api';

const ProductoList = () => {
  const [productos, setProductos] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Estado para filtros y paginación
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    categoria: '',
    estado: '',
    activo: true
  });
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);

  // Cargar productos y categorías al montar el componente
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Cargar categorías
        const categoriasResponse = await inventarioService.getCategorias();
        setCategorias(categoriasResponse.data.results);
        
        // Cargar productos con filtros
        await fetchProductos();
      } catch (err) {
        setError('Error al cargar los datos');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);

  // Cargar productos cuando cambian los filtros o la página
  useEffect(() => {
    if (!loading) {
      fetchProductos();
    }
  }, [currentPage, filters]);

  // Función para cargar productos
  const fetchProductos = async () => {
    try {
      setLoading(true);
      
      const params = {
        page: currentPage,
        search: searchTerm,
        ...filters
      };
      
      const response = await inventarioService.getProductos(params);
      setProductos(response.data.results);
      setTotalPages(Math.ceil(response.data.count / 10));
    } catch (err) {
      setError('Error al cargar los productos');
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
    fetchProductos();
  };

  // Manejar cambio de página
  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  // Renderizar estado del producto
  const renderEstado = (estado) => {
    switch (estado) {
      case 'disponible':
        return <Badge bg="success">Disponible</Badge>;
      case 'agotado':
        return <Badge bg="danger">Agotado</Badge>;
      case 'descontinuado':
        return <Badge bg="secondary">Descontinuado</Badge>;
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

  if (loading && productos.length === 0) {
    return (
      <Container>
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Cargando...</span>
          </div>
          <p className="mt-3">Cargando productos...</p>
        </div>
      </Container>
    );
  }

  return (
    <Container fluid>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 className="h3">Productos</h1>
        <Link to="/inventario/productos/nuevo" className="btn btn-primary">
          <FaPlus className="me-2" /> Nuevo Producto
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
              <Col md={4}>
                <Form.Group>
                  <Form.Label>Buscar</Form.Label>
                  <Form.Control
                    type="text"
                    placeholder="Nombre, código o descripción"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </Form.Group>
              </Col>
              
              <Col md={3}>
                <Form.Group>
                  <Form.Label>Categoría</Form.Label>
                  <Form.Select
                    name="categoria"
                    value={filters.categoria}
                    onChange={handleFilterChange}
                  >
                    <option value="">Todas</option>
                    {categorias.map(categoria => (
                      <option key={categoria.id} value={categoria.id}>
                        {categoria.nombre}
                      </option>
                    ))}
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
                    <option value="disponible">Disponible</option>
                    <option value="agotado">Agotado</option>
                    <option value="descontinuado">Descontinuado</option>
                  </Form.Select>
                </Form.Group>
              </Col>
              
              <Col md={2} className="d-flex align-items-end">
                <Button type="submit" variant="primary" className="w-100">
                  <FaSearch className="me-2" /> Filtrar
                </Button>
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
                  <th>Código</th>
                  <th>Nombre</th>
                  <th>Categoría</th>
                  <th>Stock</th>
                  <th>Precio Compra</th>
                  <th>Precio Venta</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {productos.length > 0 ? (
                  productos.map(producto => (
                    <tr key={producto.id}>
                      <td>{producto.codigo}</td>
                      <td>{producto.nombre}</td>
                      <td>{producto.categoria_nombre}</td>
                      <td>
                        {producto.stock}
                        {producto.stock <= producto.stock_minimo && (
                          <Badge bg="danger" className="ms-2">Bajo</Badge>
                        )}
                      </td>
                      <td>${producto.precio_compra.toFixed(2)}</td>
                      <td>${producto.precio_venta.toFixed(2)}</td>
                      <td>{renderEstado(producto.estado)}</td>
                      <td>
                        <div className="btn-group">
                          <Link 
                            to={`/inventario/productos/${producto.id}`}
                            className="btn btn-sm btn-info"
                            title="Ver detalles"
                          >
                            <FaEye />
                          </Link>
                          <Link 
                            to={`/inventario/productos/${producto.id}/editar`}
                            className="btn btn-sm btn-warning"
                            title="Editar"
                          >
                            <FaEdit />
                          </Link>
                          <Link 
                            to={`/inventario/productos/${producto.id}/eliminar`}
                            className="btn btn-sm btn-danger"
                            title="Eliminar"
                          >
                            <FaTrash />
                          </Link>
                        </div>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="8" className="text-center py-4">
                      No se encontraron productos
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

export default ProductoList;