import React, { useState } from 'react';
import { Form, Button, InputGroup } from 'react-bootstrap';
import { FaSearch, FaTimes } from 'react-icons/fa';
import PropTypes from 'prop-types';
import useDebounce from '../../hooks/useDebounce';

/**
 * Componente de barra de búsqueda reutilizable
 */
const SearchBar = ({ 
  onSearch, 
  placeholder = 'Buscar...', 
  buttonText = null,
  debounceTime = 500,
  initialValue = '',
  autoSearch = false
}) => {
  const [searchTerm, setSearchTerm] = useState(initialValue);
  const debouncedSearchTerm = useDebounce(searchTerm, debounceTime);
  
  // Efecto para búsqueda automática
  React.useEffect(() => {
    if (autoSearch && debouncedSearchTerm !== initialValue) {
      onSearch(debouncedSearchTerm);
    }
  }, [debouncedSearchTerm, autoSearch, onSearch, initialValue]);
  
  // Manejar envío del formulario
  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch(searchTerm);
  };
  
  // Limpiar búsqueda
  const handleClear = () => {
    setSearchTerm('');
    onSearch('');
  };
  
  return (
    <Form onSubmit={handleSubmit}>
      <InputGroup>
        <Form.Control
          type="text"
          placeholder={placeholder}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          aria-label={placeholder}
        />
        
        {searchTerm && (
          <Button 
            variant="outline-secondary" 
            onClick={handleClear}
            title="Limpiar búsqueda"
          >
            <FaTimes />
          </Button>
        )}
        
        <Button 
          variant="primary" 
          type="submit"
          disabled={!searchTerm.trim()}
        >
          <FaSearch className={buttonText ? 'me-2' : ''} />
          {buttonText}
        </Button>
      </InputGroup>
    </Form>
  );
};

SearchBar.propTypes = {
  onSearch: PropTypes.func.isRequired,
  placeholder: PropTypes.string,
  buttonText: PropTypes.string,
  debounceTime: PropTypes.number,
  initialValue: PropTypes.string,
  autoSearch: PropTypes.bool
};

export default SearchBar;