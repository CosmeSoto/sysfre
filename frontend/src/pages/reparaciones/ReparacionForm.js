import React, { useState, useEffect } from 'react';
import { Container, Card, Form, Button, Row, Col, Alert } from 'react-bootstrap';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Formik } from 'formik';
import * as Yup from 'yup';
import { reparacionesService, clientesService } from '../../services/api';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import ErrorMessage from '../../components/common/ErrorMessage';
import FormField from '../../components/common/FormField';
import SearchBar from '../../components/common/SearchBar';
import { toast } from 'react-toastify';

const ReparacionForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [reparacion, setReparacion] = useState(null);
  const [loading, setLoading] = useState(id ? true : false);
  const [error, setError] = useState(null);
  const [clientes, setClientes] = useState([]);
  const [clienteSeleccionado, setClienteSeleccionado] = useState(null);
  const [searchingCliente, setSearchingCliente] = useState(false);
  const [clienteSearch, setClienteSearch] = useState('');
  const isEditing = !!id;

  // Cargar datos de la reparación si estamos editando
  useEffect(() => {
    if (isEditing) {
      const fetchReparacion = async () => {
        try {
          const response = await reparacionesService.getReparacion(id);
          setReparacion(response.data);
          setClienteSeleccionado(response.data.cliente);
        } catch (err) {
          setError('Error al cargar los datos de la reparación');
          console.error(err);
        } finally {
          setLoading(false);
        }
      };

      fetchReparacion();
    }
  }, [id, isEditing]);

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
  const handleSelectCliente = (cliente) => {
    setClienteSeleccionado(cliente);
    setClientes([]);
    setClienteSearch('');
  };

  // Esquema de validación
  const validationSchema = Yup.object().shape({
    cliente_id: Yup.number()
      .required('El cliente es requerido'),
    equipo: Yup.string()
      .required('El equipo es requerido')
      .min(3, 'El equipo debe tener al menos 3 caracteres'),
    marca: Yup.string()
      .required('La marca es requerida'),
    modelo: Yup.string()
      .required('El modelo es requerido'),
    numero_serie: Yup.string(),
    problema_reportado: Yup.string()
      .required('El problema reportado es requerido')
      .min(10, 'La descripción del problema debe tener al menos 10 caracteres'),
    fecha_recepcion: Yup.date()
      .required('La fecha de recepción es requerida'),
    fecha_entrega_estimada: Yup.date()
      .required('La fecha estimada de entrega es requerida')
      .min(
        Yup.ref('fecha_recepcion'),
        'La fecha estimada de entrega debe ser posterior a la fecha de recepción'
      ),
    costo_diagnostico: Yup.number()
      .required('El costo de diagnóstico es requerido')
      .min(0, 'El costo de diagnóstico debe ser mayor o igual a 0'),
    costo_mano_obra: Yup.number()
      .required('El costo de mano de obra es requerido')
      .min(0, 'El costo de mano de obra debe ser mayor o igual a 0'),
    tecnico_id: Yup.number(),
    notas: Yup.string()
  });

  // Valores iniciales del formulario
  const initialValues = {
    cliente_id: reparacion?.cliente?.id || clienteSeleccionado?.id || '',
    equipo: reparacion?.equipo || '',
    marca: reparacion?.marca || '',
    modelo: reparacion?.modelo || '',
    numero_serie: reparacion?.numero_serie || '',
    problema_reportado: reparacion?.problema_reportado || '',
    fecha_recepcion: reparacion?.fecha_recepcion ? reparacion.fecha_recepcion.substring(0, 10) : new Date().toISOString().substring(0, 10),
    fecha_entrega_estimada: reparacion?.fecha_entrega_estimada ? reparacion.fecha_entrega_estimada.substring(0, 10) : '',
    costo_diagnostico: reparacion?.costo_diagnostico || 0,
    costo_mano_obra: reparacion?.costo_mano_obra || 0,
    tecnico_id: reparacion?.tecnico_id || '',
    notas: reparacion?.notas || ''
  };

  // Manejar envío del formulario
  const handleSubmit = async (values, { setSubmitting }) => {
    try {
      if (isEditing) {
        await reparacionesService.updateReparacion(id, values);
        toast.success('Reparación actualizada correctamente');
      } else {
        const response = await reparacionesService.createReparacion(values);
        toast.success('Reparación creada correctamente');
        navigate(`/reparaciones/${response.data.id}`);
        return;
      }
      navigate(`/reparaciones/${id}`);
    } catch (err) {
      setError(
        err.response?.data?.detail || 
        'Error al guardar la reparación. Por favor, inténtelo de nuevo.'
      );
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <LoadingSpinner text="Cargando datos de la reparación..." />;
  }

  return (
    <Container fluid>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 className="h3">{isEditing ? 'Editar Reparación' : 'Nueva Reparación'}</h1>
        <Link to={isEditing ? `/reparaciones/${id}` : '/reparaciones'} className="btn btn-secondary">
          Volver
        </Link>
      </div>

      <ErrorMessage error={error} />

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
        }) => (
          <Form onSubmit={handleSubmit}>
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
                      {!isEditing && (
                        <Button 
                          variant="outline-secondary"
                          onClick={() => {
                            setClienteSeleccionado(null);
                            setFieldValue('cliente_id', '');
                          }}
                        >
                          Cambiar Cliente
                        </Button>
                      )}
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
                            {searchingCliente ? 'Buscando...' : 'Buscar'}
                          </Button>
                        </div>
                      </Form.Group>
                    </div>
                    
                    {clientes.length > 0 && (
                      <div className="table-responsive">
                        <table className="table table-sm table-hover">
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
                                    onClick={() => {
                                      handleSelectCliente(cliente);
                                      setFieldValue('cliente_id', cliente.id);
                                    }}
                                  >
                                    Seleccionar
                                  </Button>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                    
                    {touched.cliente_id && errors.cliente_id && (
                      <div className="text-danger mt-2">
                        {errors.cliente_id}
                      </div>
                    )}
                    
                    <div className="mt-3">
                      <Link to="/clientes/nuevo" className="btn btn-outline-primary">
                        Crear Nuevo Cliente
                      </Link>
                    </div>
                  </div>
                )}
              </Card.Body>
            </Card>

            <Card className="mb-4">
              <Card.Header>
                <h5 className="card-title mb-0">Información del Equipo</h5>
              </Card.Header>
              <Card.Body>
                <Row>
                  <Col md={6}>
                    <FormField
                      name="equipo"
                      label="Equipo"
                      type="text"
                      placeholder="Ej: Laptop, Impresora, etc."
                      value={values.equipo}
                      onChange={handleChange}
                      onBlur={handleBlur}
                      error={errors.equipo}
                      touched={touched.equipo}
                      required
                    />
                  </Col>
                  <Col md={6}>
                    <FormField
                      name="marca"
                      label="Marca"
                      type="text"
                      placeholder="Ej: HP, Dell, etc."
                      value={values.marca}
                      onChange={handleChange}
                      onBlur={handleBlur}
                      error={errors.marca}
                      touched={touched.marca}
                      required
                    />
                  </Col>
                </Row>
                
                <Row>
                  <Col md={6}>
                    <FormField
                      name="modelo"
                      label="Modelo"
                      type="text"
                      placeholder="Ej: Pavilion 15, etc."
                      value={values.modelo}
                      onChange={handleChange}
                      onBlur={handleBlur}
                      error={errors.modelo}
                      touched={touched.modelo}
                      required
                    />
                  </Col>
                  <Col md={6}>
                    <FormField
                      name="numero_serie"
                      label="Número de Serie"
                      type="text"
                      placeholder="Número de serie del equipo"
                      value={values.numero_serie}
                      onChange={handleChange}
                      onBlur={handleBlur}
                      error={errors.numero_serie}
                      touched={touched.numero_serie}
                    />
                  </Col>
                </Row>
                
                <FormField
                  name="problema_reportado"
                  label="Problema Reportado"
                  type="textarea"
                  placeholder="Descripción del problema reportado por el cliente"
                  value={values.problema_reportado}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  error={errors.problema_reportado}
                  touched={touched.problema_reportado}
                  required
                  rows={4}
                />
              </Card.Body>
            </Card>

            <Card className="mb-4">
              <Card.Header>
                <h5 className="card-title mb-0">Información de la Reparación</h5>
              </Card.Header>
              <Card.Body>
                <Row>
                  <Col md={6}>
                    <FormField
                      name="fecha_recepcion"
                      label="Fecha de Recepción"
                      type="date"
                      value={values.fecha_recepcion}
                      onChange={handleChange}
                      onBlur={handleBlur}
                      error={errors.fecha_recepcion}
                      touched={touched.fecha_recepcion}
                      required
                    />
                  </Col>
                  <Col md={6}>
                    <FormField
                      name="fecha_entrega_estimada"
                      label="Fecha Estimada de Entrega"
                      type="date"
                      value={values.fecha_entrega_estimada}
                      onChange={handleChange}
                      onBlur={handleBlur}
                      error={errors.fecha_entrega_estimada}
                      touched={touched.fecha_entrega_estimada}
                      required
                    />
                  </Col>
                </Row>
                
                <Row>
                  <Col md={6}>
                    <FormField
                      name="costo_diagnostico"
                      label="Costo de Diagnóstico"
                      type="number"
                      value={values.costo_diagnostico}
                      onChange={handleChange}
                      onBlur={handleBlur}
                      error={errors.costo_diagnostico}
                      touched={touched.costo_diagnostico}
                      required
                      min="0"
                      step="0.01"
                      prepend="$"
                    />
                  </Col>
                  <Col md={6}>
                    <FormField
                      name="costo_mano_obra"
                      label="Costo de Mano de Obra"
                      type="number"
                      value={values.costo_mano_obra}
                      onChange={handleChange}
                      onBlur={handleBlur}
                      error={errors.costo_mano_obra}
                      touched={touched.costo_mano_obra}
                      required
                      min="0"
                      step="0.01"
                      prepend="$"
                    />
                  </Col>
                </Row>
                
                <FormField
                  name="tecnico_id"
                  label="Técnico Asignado"
                  type="select"
                  value={values.tecnico_id}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  error={errors.tecnico_id}
                  touched={touched.tecnico_id}
                  options={[
                    { value: 1, label: 'Juan Pérez' },
                    { value: 2, label: 'María López' },
                    { value: 3, label: 'Carlos Rodríguez' }
                  ]}
                />
                
                <FormField
                  name="notas"
                  label="Notas Adicionales"
                  type="textarea"
                  placeholder="Notas adicionales sobre la reparación"
                  value={values.notas}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  error={errors.notas}
                  touched={touched.notas}
                  rows={3}
                />
              </Card.Body>
            </Card>

            <div className="d-flex justify-content-end mb-4">
              <Button 
                variant="secondary" 
                className="me-2"
                as={Link}
                to={isEditing ? `/reparaciones/${id}` : '/reparaciones'}
              >
                Cancelar
              </Button>
              <Button 
                variant="primary" 
                type="submit" 
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Guardando...' : 'Guardar'}
              </Button>
            </div>
          </Form>
        )}
      </Formik>
    </Container>
  );
};

export default ReparacionForm;