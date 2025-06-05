import React from 'react';
import { Alert } from 'react-bootstrap';
import PropTypes from 'prop-types';

/**
 * Componente de mensaje de error reutilizable
 */
const ErrorMessage = ({ 
  error, 
  title = 'Error', 
  variant = 'danger',
  dismissible = false,
  onClose = null
}) => {
  if (!error) return null;
  
  return (
    <Alert 
      variant={variant} 
      dismissible={dismissible}
      onClose={onClose}
    >
      {title && <Alert.Heading>{title}</Alert.Heading>}
      {typeof error === 'string' ? error : 'Se ha producido un error inesperado.'}
    </Alert>
  );
};

ErrorMessage.propTypes = {
  error: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.object,
    PropTypes.bool
  ]),
  title: PropTypes.string,
  variant: PropTypes.string,
  dismissible: PropTypes.bool,
  onClose: PropTypes.func
};

export default ErrorMessage;