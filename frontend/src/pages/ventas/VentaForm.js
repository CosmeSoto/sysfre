import React, { useState, useEffect } from 'react';
import { Container, Card, Form, Button, Row, Col, Table, Alert } from 'react-bootstrap';
import { useNavigate, Link, useSearchParams } from 'react-router-dom';
import { Formik, FieldArray, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import { FaPlus, FaTrash, FaSearch } from 'react-icons/fa';
import { ventasService, clientesService, inventarioService } from '../../services/api';
import { toast } from 'react-toastify';

const VentaForm = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const clienteId = searchParams.get('cliente');
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [clientes, setClientes] = useState([]);
  const [productos, setProductos] = useState([]);
  const [clienteSeleccionado, setClienteSeleccionado] = useState(null);
  const [direcciones, setDirecciones] = useState([]);
  const [searchingCliente, setSearchingCliente] = useState(false);
  const [clienteSearch, setClienteSearch] = useState('');
  const [productSearch, setProductSearch] = useState('');
  const [productosEncontrados, setProductosEncontrados] = useState([]);
  const [searchingProduct, setSearchingProduct] = useState(false);

  // Cargar cliente si viene en la URL
  useEffect(() => {
    if (clienteId) {
      const fetchCliente = async () => {
        try {
          const response = await clientesService.getCliente(clienteId);
          setClienteSeleccionado(response.data);
          
          // Cargar direcciones del cliente
          const direccionesResponse = await clientesService.getDirecciones({ cliente: clienteId });
          setDirecciones(direccionesResponse.data.results);
        } catch (err) {
          console.error('Error al cargar el cliente:', err);
        }
      };
      
      fetchCliente();
    }
  }, [clienteId]);

  // Buscar clientes
  const handleClienteSearch = async () => {
    if (!clienteSearch.trim()) return;
    
    try {
      setSearchingCliente(true);
      const response = await clientesService.buscarClientes(clienteSearch);
      setClientes(response.data);
    } catch (err) {
      console.error('Error al buscar clientes:', err);
    } finally {
      setSearchingCliente(false);
    }
  };

  // Seleccionar cliente
  const handleSelectCliente = async (cliente) => {
    setClienteSeleccionado(cliente);
    setClientes([]);
    setClienteSearch('');
    
    try {
      // Cargar direcciones del cliente
      const response = await clientesService.getDirecciones({ cliente: cliente.id });
      setDirecciones(response.data.results);
    } catch (err) {
      console.error('Error al cargar direcciones:', err);
    }
  };

  // Buscar productos
  const handleProductSearch = async () => {
    if (!productSearch.trim()) return;
    
    try {
      setSearchingProduct(true);
      const response = await inventarioService.getProductos({ search: productSearch });
      setProductosEncontrados(response.data.results);
    } catch (err) {
      console.error('Error al buscar productos:', err);
    } finally {
      setSearchingProduct(false);
    }
  };

  // Esquema de validación
  const validationSchema = Yup.object().shape({
    cliente_id: Yup.number()
      .required('El cliente es requerido'),
    tipo: Yup.string()
      .required('El tipo de documento es requerido'),
    items: Yup.array()
      .of(
        Yup.object().shape({
          producto_id: Yup.number()
            .required('El producto es requerido'),
          cantidad: Yup.number()
            .required('La cantidad es requerida')
            .positive('La cantidad debe ser positiva'),
          precio_unitario: Yup.number()
            .required('El precio es requerido')
            .positive('El precio debe ser positivo'),
          descuento: Yup.number()
            .min(0, 'El descuento no puede ser negativo')
        })
      )
      .min(1, 'Debe agregar al menos un producto'),
    direccion_facturacion_id: Yup.number()
      .nullable(),
    direccion_envio_id: Yup.number()
      .nullable(),
    notas: Yup.string()
  });

  // Valores iniciales del formulario
  const initialValues = {
    cliente_id: clienteSeleccionado?.id || '',
    tipo: 'factura',
    items: [],
    direccion_facturacion_id: '',
    direccion_envio_id: '',
    notas: ''
  };

  // Calcular totales
  const calcularTotales = (items) => {
    let subtotal = 0;
    let iva = 0;
    let descuento = 0;
    
    items.forEach(item => {
      const itemSubtotal = item.cantidad * item.precio_unitario;
      const itemDescuento = item.descuento || 0;
      const itemIva = (itemSubtotal - itemDescuento) * 0.12; // 12% IVA
      
      subtotal += itemSubtotal;
      descuento += itemDescuento;
      iva += itemIva;
    });
    
    const total = subtotal - descuento + iva;
    
    return {
      subtotal: subtotal.toFixed(2),
      descuento: descuento.toFixed(2),
      iva: iva.toFixed(2),
      total: total.toFixed(2)
    };
  };

  // Manejar envío del formulario
  const handleSubmit = async (values, { setSubmitting }) => {
    try {
      setLoading(true);
      const response = await ventasService.crearVenta(values);
      toast.success('Venta creada correctamente');
      navigate(`/ventas/${response.data.id}`);
    } catch (err) {
      setError(
        err.response?.data?.detail || 
        'Error al crear la venta. Por favor, inténtelo de nuevo.'
      );
      console.error(err);
    } finally {
      setSubmitting(false);
      setLoading(false);
    }
  };

  return (
    <Container fluid>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 className="h3">Nueva Venta</h1>
        <Link to="/ventas" className="btn btn-secondary">
          Volver
        </Link>
      </div>
      
      {error && (
        <Alert variant="danger" className="mb-4">
          {error}
        </Alert>
      )}
      
      <Formik
        initialValues={initialValues}
        validationSchema={validationSchema}
        onSubmit={handleSubmit}
        enableReinitialize
      >
        {({
          values,
          errors,
          touched,
          handleChange,
          handleBlur,
          handleSubmit,
          isSubmitting,
          setFieldValue
        }) => {
          const totales = calcularTotales(values.items);
          
          return (
            <Form onSubmit={handleSubmit}>
              <Row>
                <Col lg={8}>
                  <Card className="mb-4">
                    <Card.Header>
                      <h5 className="card-title mb-0">Cliente</h5>
                    </Card.Header>
                    <Card.Body>
                      {clienteSeleccionado ? (
                        <div className="mb-3">
                          <div className="d-flex justify-content-between align-items-center">
                            <div>
                              <h5>{clienteSeleccionado.nombres} {clienteSeleccionado.apellidos}</h5>
                              <p className="mb-1">
                                <strong>{clienteSeleccionado.tipo_identificacion}:</strong> {clienteSeleccionado.identificacion}
                              </p>
                              <p className="mb-1">
                                <strong>Email:</strong> {clienteSeleccionado.email}
                              </p>
                              <p className="mb-0">
                                <strong>Teléfono:</strong> {clienteSeleccionado.telefono}
                              </p>
                            </div>
                            <Button 
                              variant="outline-secondary"
                              onClick={() => {
                                setClienteSeleccionado(null);
                                setFieldValue('cliente_id', '');
                                setDirecciones([]);
                              }}
                            >
                              Cambiar Cliente
                            </Button>
                          </div>
                          
                          <input 
                            type="hidden" 
                            name="cliente_id" 
                            value={clienteSeleccionado.id} 
                          />
                        </div>
                      ) : (
                        <div>
                          <div className="mb-3">
                            <Form.Group>
                              <Form.Label>Buscar Cliente</Form.Label>
                              <div className="d-flex">
                                <Form.Control
                                  type="text"
                                  placeholder="Nombre, identificación o email"
                                  value={clienteSearch}
                                  onChange={(e) => setClienteSearch(e.target.value)}
                                  className="me-2"
                                />
                                <Button 
                                  variant="primary"
                                  onClick={handleClienteSearch}
                                  disabled={searchingCliente}
                                >
                                  <FaSearch /> {searchingCliente ? 'Buscando...' : 'Buscar'}
                                </Button>
                              </div>
                            </Form.Group>
                          </div>
                          
                          {clientes.length > 0 && (
                            <div className="table-responsive">
                              <Table striped hover size="sm">
                                <thead>
                                  <tr>
                                    <th>Identificación</th>
                                    <th>Nombres</th>
                                    <th>Apellidos</th>
                                    <th>Email</th>
                                    <th>Acción</th>
                                  </tr>
                                </thead>
                                <tbody>
                                  {clientes.map(cliente => (
                                    <tr key={cliente.id}>
                                      <td>{cliente.identificacion}</td>
                                      <td>{cliente.nombres}</td>
                                      <td>{cliente.apellidos}</td>
                                      <td>{cliente.email}</td>
                                      <td>
                                        <Button 
                                          variant="primary" 
                                          size="sm"
                                          onClick={() => handleSelectCliente(cliente)}
                                        >
                                          Seleccionar
                                        </Button>
                                      </td>
                                    </tr>
                                  ))}
                                </tbody>
                              </Table>
                            </div>
                          )}
                          
                          {touched.cliente_id && errors.cliente_id && (
                            <div className="text-danger mt-2">
                              {errors.cliente_id}
                            </div>
                          )}
                          
                          <div className="mt-3">
                            <Link to="/clientes/nuevo" className="btn btn-outline-primary">
                              <FaPlus className="me-2" /> Crear Nuevo Cliente
                            </Link>
                          </div>
                        </div>
                      )}
                    </Card.Body>
                  </Card>
                  
                  <Card className="mb-4">
                    <Card.Header className="d-flex justify-content-between align-items-center">
                      <h5 className="card-title mb-0">Productos</h5>
                    </Card.Header>
                    <Card.Body>
                      <div className="mb-3">
                        <Form.Group>
                          <Form.Label>Buscar Producto</Form.Label>
                          <div className="d-flex">
                            <Form.Control
                              type="text"
                              placeholder="Nombre, código o descripción"
                              value={productSearch}
                              onChange={(e) => setProductSearch(e.target.value)}
                              className="me-2"
                            />
                            <Button 
                              variant="primary"
                              onClick={handleProductSearch}
                              disabled={searchingProduct}
                            >
                              <FaSearch /> {searchingProduct ? 'Buscando...' : 'Buscar'}
                            </Button>
                          </div>
                        </Form.Group>
                      </div>
                      
                      {productosEncontrados.length > 0 && (
                        <div className="table-responsive mb-3">
                          <Table striped hover size="sm">
                            <thead>
                              <tr>
                                <th>Código</th>
                                <th>Nombre</th>
                                <th>Precio</th>
                                <th>Stock</th>
                                <th>Acción</th>
                              </tr>
                            </thead>
                            <tbody>
                              {productosEncontrados.map(producto => (
                                <tr key={producto.id}>
                                  <td>{producto.codigo}</td>
                                  <td>{producto.nombre}</td>
                                  <td>${producto.precio_venta.toFixed(2)}</td>
                                  <td>{producto.stock}</td>
                                  <td>
                                    <Button 
                                      variant="primary" 
                                      size="sm"
                                      onClick={() => {
                                        // Verificar si el producto ya está en la lista
                                        const existingIndex = values.items.findIndex(
                                          item => item.producto_id === producto.id
                                        );
                                        
                                        if (existingIndex >= 0) {
                                          // Incrementar cantidad si ya existe
                                          const newItems = [...values.items];
                                          newItems[existingIndex].cantidad += 1;
                                          setFieldValue('items', newItems);
                                        } else {
                                          // Agregar nuevo item
                                          setFieldValue('items', [
                                            ...values.items,
                                            {
                                              producto_id: producto.id,
                                              producto_nombre: producto.nombre,
                                              cantidad: 1,
                                              precio_unitario: producto.precio_venta,
                                              descuento: 0
                                            }
                                          ]);
                                        }
                                        
                                        // Limpiar búsqueda
                                        setProductosEncontrados([]);
                                        setProductSearch('');
                                      }}
                                    >
                                      Agregar
                                    </Button>
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </Table>
                        </div>
                      )}
                      
                      <FieldArray name="items">
                        {({ remove, push }) => (
                          <div>
                            {values.items.length > 0 ? (
                              <div className="table-responsive">
                                <Table striped>
                                  <thead>
                                    <tr>
                                      <th>Producto</th>
                                      <th>Cantidad</th>
                                      <th>Precio</th>
                                      <th>Descuento</th>
                                      <th>Subtotal</th>
                                      <th>Acción</th>
                                    </tr>
                                  </thead>
                                  <tbody>
                                    {values.items.map((item, index) => (
                                      <tr key={index}>
                                        <td>{item.producto_nombre}</td>
                                        <td>
                                          <Form.Control
                                            type="number"
                                            name={`items.${index}.cantidad`}
                                            value={item.cantidad}
                                            onChange={handleChange}
                                            onBlur={handleBlur}
                                            min="1"
                                            style={{ width: '80px' }}
                                          />
                                          <ErrorMessage
                                            name={`items.${index}.cantidad`}
                                            component="div"
                                            className="text-danger"
                                          />
                                        </td>
                                        <td>
                                          <Form.Control
                                            type="number"
                                            name={`items.${index}.precio_unitario`}
                                            value={item.precio_unitario}
                                            onChange={handleChange}
                                            onBlur={handleBlur}
                                            step="0.01"
                                            style={{ width: '100px' }}
                                          />
                                          <ErrorMessage
                                            name={`items.${index}.precio_unitario`}
                                            component="div"
                                            className="text-danger"
                                          />
                                        </td>
                                        <td>
                                          <Form.Control
                                            type="number"
                                            name={`items.${index}.descuento`}
                                            value={item.descuento}
                                            onChange={handleChange}
                                            onBlur={handleBlur}
                                            step="0.01"
                                            min="0"
                                            style={{ width: '100px' }}
                                          />
                                          <ErrorMessage
                                            name={`items.${index}.descuento`}
                                            component="div"
                                            className="text-danger"
                                          />
                                        </td>
                                        <td>
                                          ${((item.cantidad * item.precio_unitario) - (item.descuento || 0)).toFixed(2)}
                                        </td>
                                        <td>
                                          <Button
                                            variant="danger"
                                            size="sm"
                                            onClick={() => remove(index)}
                                          >
                                            <FaTrash />
                                          </Button>
                                        </td>
                                      </tr>
                                    ))}
                                  </tbody>
                                </Table>
                              </div>
                            ) : (
                              <div className="text-center py-4">
                                <p>No hay productos agregados</p>
                                <Button 
                                  variant="primary" 
                                  onClick={() => setProductSearch('')}
                                >
                                  Buscar Productos
                                </Button>
                              </div>
                            )}
                            
                            {touched.items && errors.items && typeof errors.items === 'string' && (
                              <div className="text-danger mt-2">
                                {errors.items}
                              </div>
                            )}
                          </div>
                        )}
                      </FieldArray>
                    </Card.Body>
                  </Card>
                </Col>
                
                <Col lg={4}>
                  <Card className="mb-4">
                    <Card.Header>
                      <h5 className="card-title mb-0">Detalles de la Venta</h5>
                    </Card.Header>
                    <Card.Body>
                      <Form.Group className="mb-3">
                        <Form.Label>Tipo de Documento</Form.Label>
                        <Form.Select
                          name="tipo"
                          value={values.tipo}
                          onChange={handleChange}
                          onBlur={handleBlur}
                          isInvalid={touched.tipo && errors.tipo}
                        >
                          <option value="factura">Factura</option>
                          <option value="nota_venta">Nota de Venta</option>
                        </Form.Select>
                        <Form.Control.Feedback type="invalid">
                          {errors.tipo}
                        </Form.Control.Feedback>
                      </Form.Group>
                      
                      {direcciones.length > 0 && (
                        <>
                          <Form.Group className="mb-3">
                            <Form.Label>Dirección de Facturación</Form.Label>
                            <Form.Select
                              name="direccion_facturacion_id"
                              value={values.direccion_facturacion_id}
                              onChange={handleChange}
                              onBlur={handleBlur}
                            >
                              <option value="">Seleccione una dirección</option>
                              {direcciones.map(dir => (
                                <option key={dir.id} value={dir.id}>
                                  {dir.nombre}: {dir.direccion}, {dir.ciudad}
                                </option>
                              ))}
                            </Form.Select>
                          </Form.Group>
                          
                          <Form.Group className="mb-3">
                            <Form.Label>Dirección de Envío</Form.Label>
                            <Form.Select
                              name="direccion_envio_id"
                              value={values.direccion_envio_id}
                              onChange={handleChange}
                              onBlur={handleBlur}
                            >
                              <option value="">Seleccione una dirección</option>
                              {direcciones.map(dir => (
                                <option key={dir.id} value={dir.id}>
                                  {dir.nombre}: {dir.direccion}, {dir.ciudad}
                                </option>
                              ))}
                            </Form.Select>
                          </Form.Group>
                        </>
                      )}
                      
                      <Form.Group className="mb-3">
                        <Form.Label>Notas</Form.Label>
                        <Form.Control
                          as="textarea"
                          rows={3}
                          name="notas"
                          value={values.notas}
                          onChange={handleChange}
                          onBlur={handleBlur}
                        />
                      </Form.Group>
                      
                      <hr />
                      
                      <div className="d-flex justify-content-between mb-2">
                        <span>Subtotal:</span>
                        <span>${totales.subtotal}</span>
                      </div>
                      
                      <div className="d-flex justify-content-between mb-2">
                        <span>Descuento:</span>
                        <span>${totales.descuento}</span>
                      </div>
                      
                      <div className="d-flex justify-content-between mb-2">
                        <span>IVA (12%):</span>
                        <span>${totales.iva}</span>
                      </div>
                      
                      <div className="d-flex justify-content-between mb-3">
                        <span className="fw-bold">Total:</span>
                        <span className="fw-bold">${totales.total}</span>
                      </div>
                      
                      <div className="d-grid gap-2">
                        <Button 
                          variant="primary" 
                          type="submit" 
                          disabled={isSubmitting || loading || values.items.length === 0 || !values.cliente_id}
                        >
                          {isSubmitting || loading ? 'Guardando...' : 'Crear Venta'}
                        </Button>
                        <Button 
                          variant="outline-secondary" 
                          as={Link}
                          to="/ventas"
                        >
                          Cancelar
                        </Button>
                      </div>
                    </Card.Body>
                  </Card>
                </Col>
              </Row>
            </Form>
          );
        }}
      </Formik>
    </Container>
  );
};

export default VentaForm;