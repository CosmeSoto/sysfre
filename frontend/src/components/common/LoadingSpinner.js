import React from 'react';
import { Spinner } from 'react-bootstrap';

const LoadingSpinner = () => {
  return (
    <div className="d-flex justify-content-center align-items-center" style={{ height: '100vh' }}>
      <Spinner animation="border" role="status" aria-label="Cargando...">
        <span className="visually-hidden">Cargando...</span>
      </Spinner>
    </div>
  );
};

export default LoadingSpinner;