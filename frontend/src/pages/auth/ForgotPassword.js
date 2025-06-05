import React, { useState } from 'react';
import { Container, Card, Form, Button, Alert } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { Formik } from 'formik';
import * as Yup from 'yup';
import { authService } from '../../services/api';

const ForgotPassword = () => {
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Esquema de validación
  const validationSchema = Yup.object().shape({
    email: Yup.string()
      .email('Ingrese un correo electrónico válido')
      .required('El correo electrónico es requerido')
  });

  // Manejar el envío del formulario
  const handleSubmit = async (values, { setSubmitting, resetForm }) => {
    try {
      setError('');
      setSuccess('');
      
      // En un caso real, esto sería una llamada a la API
      // await authService.forgotPassword(values.email);
      
      // Simular una llamada exitosa
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSuccess('Se ha enviado un enlace de recuperación a su correo electrónico.');
      resetForm();
    } catch (error) {
      setError(
        error.response?.data?.detail || 
        'Error al procesar la solicitud. Inténtelo de nuevo más tarde.'
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Container className="d-flex align-items-center justify-content-center" style={{ minHeight: '100vh' }}>
      <div style={{ width: '100%', maxWidth: '400px' }}>
        <Card>
          <Card.Header className="bg-primary text-white text-center py-3">
            <h3 className="mb-0">Recuperar Contraseña</h3>
          </Card.Header>
          <Card.Body className="p-4">
            {error && (
              <Alert variant="danger">{error}</Alert>
            )}
            
            {success && (
              <Alert variant="success">{success}</Alert>
            )}
            
            <p className="text-muted mb-4">
              Ingrese su correo electrónico y le enviaremos instrucciones para restablecer su contraseña.
            </p>
            
            <Formik
              initialValues={{ email: '' }}
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
                  <Form.Group className="mb-4">
                    <Form.Label>Correo electrónico</Form.Label>
                    <Form.Control
                      type="email"
                      name="email"
                      value={values.email}
                      onChange={handleChange}
                      onBlur={handleBlur}
                      isInvalid={touched.email && errors.email}
                      placeholder="Ingrese su correo electrónico"
                    />
                    <Form.Control.Feedback type="invalid">
                      {errors.email}
                    </Form.Control.Feedback>
                  </Form.Group>
                  
                  <div className="d-grid">
                    <Button 
                      variant="primary" 
                      type="submit" 
                      disabled={isSubmitting}
                    >
                      {isSubmitting ? 'Enviando...' : 'Enviar Instrucciones'}
                    </Button>
                  </div>
                </Form>
              )}
            </Formik>
            
            <div className="text-center mt-3">
              <Link to="/login">Volver al inicio de sesión</Link>
            </div>
          </Card.Body>
        </Card>
      </div>
    </Container>
  );
};

export default ForgotPassword;