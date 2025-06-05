import React from 'react';
import { Form, InputGroup } from 'react-bootstrap';
import PropTypes from 'prop-types';

/**
 * Componente de campo de formulario reutilizable
 */
const FormField = ({
  name,
  label,
  type = 'text',
  placeholder = '',
  value,
  onChange,
  onBlur,
  error,
  touched,
  disabled = false,
  readOnly = false,
  required = false,
  options = [],
  rows = 3,
  prepend = null,
  append = null,
  className = '',
  helpText = null,
  min = null,
  max = null,
  step = null
}) => {
  // Determinar si mostrar error
  const showError = touched && error;
  
  // Renderizar campo según el tipo
  const renderField = () => {
    const commonProps = {
      name,
      id: name,
      value,
      onChange,
      onBlur,
      disabled,
      readOnly,
      placeholder,
      isInvalid: showError,
      className
    };
    
    // Agregar props específicos según el tipo
    if (type === 'number') {
      commonProps.min = min;
      commonProps.max = max;
      commonProps.step = step;
    }
    
    // Renderizar según el tipo
    switch (type) {
      case 'select':
        return (
          <Form.Select {...commonProps}>
            {!required && <option value="">Seleccione...</option>}
            {options.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </Form.Select>
        );
        
      case 'textarea':
        return (
          <Form.Control
            {...commonProps}
            as="textarea"
            rows={rows}
          />
        );
        
      case 'checkbox':
        return (
          <Form.Check
            type="checkbox"
            name={name}
            id={name}
            label={label}
            checked={value}
            onChange={onChange}
            onBlur={onBlur}
            disabled={disabled}
            isInvalid={showError}
            className={className}
          />
        );
        
      case 'radio':
        return (
          <>
            {options.map((option) => (
              <Form.Check
                key={option.value}
                type="radio"
                name={name}
                id={`${name}-${option.value}`}
                label={option.label}
                value={option.value}
                checked={value === option.value}
                onChange={onChange}
                onBlur={onBlur}
                disabled={disabled}
                isInvalid={showError}
                className={className}
              />
            ))}
          </>
        );
        
      default:
        return (
          <Form.Control
            {...commonProps}
            type={type}
          />
        );
    }
  };
  
  // Si es checkbox, renderizar de forma diferente
  if (type === 'checkbox') {
    return (
      <Form.Group className="mb-3">
        {renderField()}
        {showError && (
          <Form.Control.Feedback type="invalid">
            {error}
          </Form.Control.Feedback>
        )}
        {helpText && <Form.Text className="text-muted">{helpText}</Form.Text>}
      </Form.Group>
    );
  }
  
  // Si es radio, renderizar de forma diferente
  if (type === 'radio') {
    return (
      <Form.Group className="mb-3">
        <Form.Label>{label}{required && <span className="text-danger">*</span>}</Form.Label>
        {renderField()}
        {showError && (
          <Form.Control.Feedback type="invalid">
            {error}
          </Form.Control.Feedback>
        )}
        {helpText && <Form.Text className="text-muted">{helpText}</Form.Text>}
      </Form.Group>
    );
  }
  
  // Renderizar campo normal
  return (
    <Form.Group className="mb-3">
      <Form.Label htmlFor={name}>
        {label}{required && <span className="text-danger">*</span>}
      </Form.Label>
      
      {(prepend || append) ? (
        <InputGroup>
          {prepend && <InputGroup.Text>{prepend}</InputGroup.Text>}
          {renderField()}
          {append && <InputGroup.Text>{append}</InputGroup.Text>}
          {showError && (
            <Form.Control.Feedback type="invalid">
              {error}
            </Form.Control.Feedback>
          )}
        </InputGroup>
      ) : (
        renderField()
      )}
      
      {showError && (
        <Form.Control.Feedback type="invalid">
          {error}
        </Form.Control.Feedback>
      )}
      
      {helpText && <Form.Text className="text-muted">{helpText}</Form.Text>}
    </Form.Group>
  );
};

FormField.propTypes = {
  name: PropTypes.string.isRequired,
  label: PropTypes.string,
  type: PropTypes.string,
  placeholder: PropTypes.string,
  value: PropTypes.any,
  onChange: PropTypes.func.isRequired,
  onBlur: PropTypes.func,
  error: PropTypes.string,
  touched: PropTypes.bool,
  disabled: PropTypes.bool,
  readOnly: PropTypes.bool,
  required: PropTypes.bool,
  options: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
      label: PropTypes.string
    })
  ),
  rows: PropTypes.number,
  prepend: PropTypes.node,
  append: PropTypes.node,
  className: PropTypes.string,
  helpText: PropTypes.string,
  min: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  max: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  step: PropTypes.oneOfType([PropTypes.string, PropTypes.number])
};

export default FormField;