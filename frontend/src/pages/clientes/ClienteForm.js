import React, { useState, useEffect } from 'react';
import { Container, Card, Form, Button, Row, Col, Alert } from 'react-bootstrap';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Formik } from 'formik';
import * as Yup from 'yup';
import { clientesService } from '../../services/api';
import { toast } from 'react-toastify';

const ClienteForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [cliente, setCliente] = useState(null);
  const [loading, setLoading] = useState(id ? true : false);
  const [error, setError] = useState(null);
  const isEditing = !!id;

  // Cargar datos del cliente si estamos editando
  useEffect(() => {
    if (isEditing) {
      const fetchCliente = async () => {
        try {
          const response = await clientesService.getCliente(id);
          setCliente(response.data);
        } catch (err) {
          setError('Error al cargar los datos del cliente');
          console.error(err);
        } finally {
          setLoading(false);
        }
      };

      fetchCliente();
    }
  }, [id, isEditing]);

  // Esquema de validación
  const validationSchema = Yup.object().shape({
    tipo_identificacion: Yup.string()
      .required('El tipo de identificación es requerido'),
    identificacion: Yup.string()
      .required('La identificación es requerida')
      .min(5, 'La identificación debe tener al menos 5 caracteres'),
    nombres: Yup.string()
      .required('Los nombres son requeridos')
      .min(2, 'Los nombres deben tener al menos 2 caracteres'),
    apellidos: Yup.string()
      .required('Los apellidos son requeridos')
      .min(2, 'Los apellidos deben tener al menos 2 caracteres'),
    email: Yup.string()
      .email('Ingrese un correo electrónico válido')
      .required('El correo electrónico es requerido'),
    telefono: Yup.string()
      .required('El teléfono es requerido'),
    direccion: Yup.string()
      .required('La dirección es requerida'),
    ciudad: Yup.string()
      .required('La ciudad es requerida'),
    provincia: Yup.string()
      .required('La provincia es requerida')
  });

  // Valores iniciales del formulario
  const initialValues = {
    tipo_identificacion: cliente?.tipo_identificacion || 'cedula',
    identificacion: cliente?.identificacion || '',
    nombres: cliente?.nombres || '',
    apellidos: cliente?.apellidos || '',
    email: cliente?.email || '',
    telefono: cliente?.telefono || '',
    direccion: cliente?.direccion || '',
    ciudad: cliente?.ciudad || '',
    provincia: cliente?.provincia || '',
    notas: cliente?.notas || ''
  };

  // Manejar envío del formulario
  const handleSubmit = async (values, { setSubmitting }) => {
    try {
      if (isEditing) {
        await clientesService.updateCliente(id, values);
        toast.success('Cliente actualizado correctamente');
      } else {
        await clientesService.createCliente(values);
        toast.success('Cliente creado correctamente');
      }
      navigate('/clientes');
    } catch (err) {
      setError(
        err.response?.data?.detail || 
        'Error al guardar el cliente. Por favor, inténtelo de nuevo.'
      );
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

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

  return (
    <Container fluid>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 className="h3">{isEditing ? 'Editar Cliente' : 'Nuevo Cliente'}</h1>
        <Link to="/clientes" className="btn btn-secondary">
          Volver
        </Link>
      </div>
      
      {error && (
        <Alert variant="danger" className="mb-4">
          {error}
        </Alert>
      )}
      
      <Card>
        <Card.Body>
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
              isSubmitting
            }) => (
              <Form onSubmit={handleSubmit}>
                <Row className="mb-3">
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Tipo de Identificación</Form.Label>
                      <Form.Select
                        name="tipo_identificacion"
                        value={values.tipo_identificacion}
                        onChange={handleChange}
                        onBlur={handleBlur}
                        isInvalid={touched.tipo_identificacion && errors.tipo_identificacion}
                      >
                        <option value="cedula">Cédula</option>
                        <option value="ruc">RUC</option>
                        <option value="pasaporte">Pasaporte</option>
                      </Form.Select>
                      <Form.Control.Feedback type="invalid">
                        {errors.tipo_identificacion}
                      </Form.Control.Feedback>
                    </Form.Group>
                  </Col>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Identificación</Form.Label>
                      <Form.Control
                        type="text"
                        name="identificacion"
                        value={values.identificacion}
                        onChange={handleChange}
                        onBlur={handleBlur}
                        isInvalid={touched.identificacion && errors.identificacion}
                      />
                      <Form.Control.Feedback type="invalid">
                        {errors.identificacion}
                      </Form.Control.Feedback>
                    </Form.Group>
                  </Col>
                </Row>
                
                <Row className="mb-3">
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Nombres</Form.Label>
                      <Form.Control
                        type="text"
                        name="nombres"
                        value={values.nombres}
                        onChange={handleChange}
                        onBlur={handleBlur}
                        isInvalid={touched.nombres && errors.nombres}
                      />
                      <Form.Control.Feedback type="invalid">
                        {errors.nombres}
                      </Form.Control.Feedback>
                    </Form.Group>
                  </Col>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Apellidos</Form.Label>
                      <Form.Control
                        type="text"
                        name="apellidos"
                        value={values.apellidos}
                        onChange={handleChange}
                        onBlur={handleBlur}
                        isInvalid={touched.apellidos && errors.apellidos}
                      />
                      <Form.Control.Feedback type="invalid">
                        {errors.apellidos}
                      </Form.Control.Feedback>
                    </Form.Group>
                  </Col>
                </Row>
                
                <Row className="mb-3">
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Email</Form.Label>
                      <Form.Control
                        type="email"
                        name="email"
                        value={values.email}
                        onChange={handleChange}
                        onBlur={handleBlur}
                        isInvalid={touched.email && errors.email}
                      />
                      <Form.Control.Feedback type="invalid">
                        {errors.email}
                      </Form.Control.Feedback>
                    </Form.Group>
                  </Col>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Teléfono</Form.Label>
                      <Form.Control
                        type="text"
                        name="telefono"
                        value={values.telefono}
                        onChange={handleChange}
                        onBlur={handleBlur}
                        isInvalid={touched.telefono && errors.telefono}
                      />
                      <Form.Control.Feedback type="invalid">
                        {errors.telefono}
                      </Form.Control.Feedback>
                    </Form.Group>
                  </Col>
                </Row>
                
                <Form.Group className="mb-3">
                  <Form.Label>Dirección</Form.Label>
                  <Form.Control
                    type="text"
                    name="direccion"
                    value={values.direccion}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    isInvalid={touched.direccion && errors.direccion}
                  />
                  <Form.Control.Feedback type="invalid">
                    {errors.direccion}
                  </Form.Control.Feedback>
                </Form.Group>
                
                <Row className="mb-3">
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Ciudad</Form.Label>
                      <Form.Control
                        type="text"
                        name="ciudad"
                        value={values.ciudad}
                        onChange={handleChange}
                        onBlur={handleBlur}
                        isInvalid={touched.ciudad && errors.ciudad}
                      />
                      <Form.Control.Feedback type="invalid">
                        {errors.ciudad}
                      </Form.Control.Feedback>
                    </Form.Group>
                  </Col>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Provincia</Form.Label>
                      <Form.Control
                        type="text"
                        name="provincia"
                        value={values.provincia}
                        onChange={handleChange}
                        onBlur={handleBlur}
                        isInvalid={touched.provincia && errors.provincia}
                      />
                      <Form.Control.Feedback type="invalid">
                        {errors.provincia}
                      </Form.Control.Feedback>
                    </Form.Group>
                  </Col>
                </Row>
                
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
                
                <div className="d-flex justify-content-end">
                  <Button 
                    variant="secondary" 
                    className="me-2"
                    as={Link}
                    to="/clientes"
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
        </Card.Body>
      </Card>
    </Container>
  );
};

export default ClienteForm;