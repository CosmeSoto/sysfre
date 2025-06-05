import React, { useState, useEffect } from 'react';
import { Container, Card, Form, Button, Row, Col, Alert } from 'react-bootstrap';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Formik } from 'formik';
import * as Yup from 'yup';
import { ventasService } from '../../services/api';
import { toast } from 'react-toastify';

const PagoForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [venta, setVenta] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchVenta = async () => {
      try {
        setLoading(true);
        const response = await ventasService.getVenta(id);
        setVenta(response.data);
        
        // Verificar si la venta está en estado pendiente
        if (response.data.estado !== 'pendiente') {
          setError(`No se puede registrar un pago para una venta en estado ${response.data.estado}`);
        }
      } catch (err) {
        setError('Error al cargar los datos de la venta');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchVenta();
  }, [id]);

  // Esquema de validación
  const validationSchema = Yup.object().shape({
    metodo: Yup.string()
      .required('El método de pago es requerido'),
    monto: Yup.number()
      .required('El monto es requerido')
      .positive('El monto debe ser positivo')
      .test(
        'not-greater-than-total',
        'El monto no puede ser mayor que el total de la venta',
        function(value) {
          return !venta || value <= venta.total;
        }
      ),
    referencia: Yup.string()
      .when('metodo', {
        is: (metodo) => metodo !== 'efectivo',
        then: Yup.string().required('La referencia es requerida para este método de pago')
      }),
    notas: Yup.string()
  });

  // Valores iniciales del formulario
  const initialValues = {
    metodo: 'efectivo',
    monto: venta?.total || 0,
    referencia: '',
    notas: ''
  };

  // Manejar envío del formulario
  const handleSubmit = async (values, { setSubmitting }) => {
    try {
      await ventasService.registrarPago(id, values);
      toast.success('Pago registrado correctamente');
      navigate(`/ventas/${id}`);
    } catch (err) {
      setError(
        err.response?.data?.detail || 
        'Error al registrar el pago. Por favor, inténtelo de nuevo.'
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
        <Link to={`/ventas/${id}`} className="btn btn-primary">
          Volver a la venta
        </Link>
      </Container>
    );
  }

  return (
    <Container fluid>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 className="h3">Registrar Pago</h1>
        <Link to={`/ventas/${id}`} className="btn btn-secondary">
          Volver
        </Link>
      </div>
      
      <Row>
        <Col lg={8}>
          <Card className="mb-4">
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
                <Col sm={4} className="fw-bold">Cliente:</Col>
                <Col sm={8}>{venta.cliente_nombre}</Col>
              </Row>
              <Row className="mb-3">
                <Col sm={4} className="fw-bold">Subtotal:</Col>
                <Col sm={8}>${venta.subtotal.toFixed(2)}</Col>
              </Row>
              <Row className="mb-3">
                <Col sm={4} className="fw-bold">IVA:</Col>
                <Col sm={8}>${venta.iva.toFixed(2)}</Col>
              </Row>
              <Row className="mb-3">
                <Col sm={4} className="fw-bold">Total:</Col>
                <Col sm={8}>${venta.total.toFixed(2)}</Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>
        
        <Col lg={4}>
          <Card>
            <Card.Header>
              <h5 className="card-title mb-0">Datos del Pago</h5>
            </Card.Header>
            <Card.Body>
              <Formik
                initialValues={initialValues}
                validationSchema={validationSchema}
                onSubmit={handleSubmit}
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
                    <Form.Group className="mb-3">
                      <Form.Label>Método de Pago</Form.Label>
                      <Form.Select
                        name="metodo"
                        value={values.metodo}
                        onChange={handleChange}
                        onBlur={handleBlur}
                        isInvalid={touched.metodo && errors.metodo}
                      >
                        <option value="efectivo">Efectivo</option>
                        <option value="tarjeta">Tarjeta de Crédito/Débito</option>
                        <option value="transferencia">Transferencia Bancaria</option>
                        <option value="cheque">Cheque</option>
                        <option value="otro">Otro</option>
                      </Form.Select>
                      <Form.Control.Feedback type="invalid">
                        {errors.metodo}
                      </Form.Control.Feedback>
                    </Form.Group>
                    
                    <Form.Group className="mb-3">
                      <Form.Label>Monto</Form.Label>
                      <Form.Control
                        type="number"
                        name="monto"
                        value={values.monto}
                        onChange={handleChange}
                        onBlur={handleBlur}
                        isInvalid={touched.monto && errors.monto}
                        step="0.01"
                        min="0.01"
                        max={venta.total}
                      />
                      <Form.Control.Feedback type="invalid">
                        {errors.monto}
                      </Form.Control.Feedback>
                    </Form.Group>
                    
                    {values.metodo !== 'efectivo' && (
                      <Form.Group className="mb-3">
                        <Form.Label>Referencia</Form.Label>
                        <Form.Control
                          type="text"
                          name="referencia"
                          value={values.referencia}
                          onChange={handleChange}
                          onBlur={handleBlur}
                          isInvalid={touched.referencia && errors.referencia}
                          placeholder={
                            values.metodo === 'tarjeta' ? 'Últimos 4 dígitos' :
                            values.metodo === 'transferencia' ? 'Número de transacción' :
                            values.metodo === 'cheque' ? 'Número de cheque' : 'Referencia'
                          }
                        />
                        <Form.Control.Feedback type="invalid">
                          {errors.referencia}
                        </Form.Control.Feedback>
                      </Form.Group>
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
                    
                    <div className="d-grid gap-2">
                      <Button 
                        variant="primary" 
                        type="submit" 
                        disabled={isSubmitting}
                      >
                        {isSubmitting ? 'Registrando...' : 'Registrar Pago'}
                      </Button>
                      <Button 
                        variant="outline-secondary" 
                        as={Link}
                        to={`/ventas/${id}`}
                      >
                        Cancelar
                      </Button>
                    </div>
                  </Form>
                )}
              </Formik>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default PagoForm;