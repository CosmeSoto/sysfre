import React, { useState, useEffect } from 'react';
import { Container, Card, Form, Button, Alert } from 'react-bootstrap';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { Formik } from 'formik';
import * as Yup from 'yup';
import { authService } from '../../services/api';

const ResetPassword = () => {
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [tokenValid, setTokenValid] = useState(true);
  const { token } = useParams();
  const navigate = useNavigate();

  // Verificar validez del token al cargar
  useEffect(() => {
    const verifyToken = async () => {
      try {
        // En un caso real, esto sería una llamada a la API
        // await authService.verifyResetToken(token);
        
        // Simular verificación de token
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Para demostración, asumimos que el token es válido
        setTokenValid(true);
      } catch (error) {
        setTokenValid(false);
        setError('El enlace de restablecimiento no es válido o ha expirado.');
      }
    };

    verifyToken();
  }, [token]);

  // Esquema de validación
  const validationSchema = Yup.object().shape({
    password: Yup.string()
      .min(8, 'La contraseña debe tener al menos 8 caracteres')
      .matches(
        /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/,
        'La contraseña debe contener al menos una letra mayúscula, una minúscula, un número y un carácter especial'
      )
      .required('La contraseña es requerida'),
    confirmPassword: Yup.string()
      .oneOf([Yup.ref('password'), null], 'Las contraseñas deben coincidir')
      .required('Confirme su contraseña')
  });

  // Manejar el envío del formulario
  const handleSubmit = async (values, { setSubmitting }) => {
    try {
      setError('');
      setSuccess('');
      
      // En un caso real, esto sería una llamada a la API
      // await authService.resetPassword(token, values.password);
      
      // Simular una llamada exitosa
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSuccess('Su contraseña ha sido restablecida correctamente.');
      
      // Redirigir al login después de 3 segundos
      setTimeout(() => {
        navigate('/login');
      }, 3000);
    } catch (error) {
      setError(
        error.response?.data?.detail || 
        'Error al restablecer la contraseña. Inténtelo de nuevo más tarde.'
      );
    } finally {
      setSubmitting(false);
    }
  };

  if (!tokenValid) {
    return (
      <Container className="d-flex align-items-center justify-content-center" style={{ minHeight: '100vh' }}>
        <div style={{ width: '100%', maxWidth: '400px' }}>
          <Card>
            <Card.Header className="bg-danger text-white text-center py-3">
              <h3 className="mb-0">Enlace Inválido</h3>
            </Card.Header>
            <Card.Body className="p-4 text-center">
              <p>El enlace de restablecimiento no es válido o ha expirado.</p>
              <Link to="/forgot-password" className="btn btn-primary mt-3">
                Solicitar un nuevo enlace
              </Link>
            </Card.Body>
          </Card>
        </div>
      </Container>
    );
  }

  return (
    <Container className="d-flex align-items-center justify-content-center" style={{ minHeight: '100vh' }}>
      <div style={{ width: '100%', maxWidth: '400px' }}>
        <Card>
          <Card.Header className="bg-primary text-white text-center py-3">
            <h3 className="mb-0">Restablecer Contraseña</h3>
          </Card.Header>
          <Card.Body className="p-4">
            {error && (
              <Alert variant="danger">{error}</Alert>
            )}
            
            {success && (
              <Alert variant="success">{success}</Alert>
            )}
            
            <Formik
              initialValues={{ password: '', confirmPassword: '' }}
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
                    <Form.Label>Nueva contraseña</Form.Label>
                    <Form.Control
                      type="password"
                      name="password"
                      value={values.password}
                      onChange={handleChange}
                      onBlur={handleBlur}
                      isInvalid={touched.password && errors.password}
                      placeholder="Ingrese su nueva contraseña"
                    />
                    <Form.Control.Feedback type="invalid">
                      {errors.password}
                    </Form.Control.Feedback>
                  </Form.Group>
                  
                  <Form.Group className="mb-4">
                    <Form.Label>Confirmar contraseña</Form.Label>
                    <Form.Control
                      type="password"
                      name="confirmPassword"
                      value={values.confirmPassword}
                      onChange={handleChange}
                      onBlur={handleBlur}
                      isInvalid={touched.confirmPassword && errors.confirmPassword}
                      placeholder="Confirme su nueva contraseña"
                    />
                    <Form.Control.Feedback type="invalid">
                      {errors.confirmPassword}
                    </Form.Control.Feedback>
                  </Form.Group>
                  
                  <div className="d-grid">
                    <Button 
                      variant="primary" 
                      type="submit" 
                      disabled={isSubmitting || success}
                    >
                      {isSubmitting ? 'Procesando...' : 'Restablecer Contraseña'}
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

export default ResetPassword;