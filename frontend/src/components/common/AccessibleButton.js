import React from 'react';
import { Button } from 'react-bootstrap';

const AccessibleButton = ({ 
  children, 
  onClick, 
  variant = 'primary', 
  ariaLabel,
  disabled = false,
  ...props 
}) => {
  return (
    <Button
      variant={variant}
      onClick={onClick}
      disabled={disabled}
      aria-label={ariaLabel || undefined}
      {...props}
    >
      {children}
    </Button>
  );
};

export default AccessibleButton;