import React from 'react';
import { Form } from 'react-bootstrap';

const AccessibleFormField = ({
  name,
  label,
  type = 'text',
  value,
  onChange,
  error,
  required = false,
  ...props
}) => {
  const id = `field-${name}`;
  
  return (
    <Form.Group className="mb-3">
      <Form.Label htmlFor={id}>
        {label}
        {required && <span className="text-danger" aria-hidden="true">*</span>}
        {required && <span className="visually-hidden">(requerido)</span>}
      </Form.Label>
      <Form.Control
        type={type}
        name={name}
        id={id}
        value={value}
        onChange={onChange}
        isInvalid={!!error}
        aria-invalid={!!error}
        aria-describedby={error ? `${id}-error` : undefined}
        required={required}
        {...props}
      />
      {error && (
        <Form.Control.Feedback type="invalid" id={`${id}-error`}>
          {error}
        </Form.Control.Feedback>
      )}
    </Form.Group>
  );
};

export default AccessibleFormField;