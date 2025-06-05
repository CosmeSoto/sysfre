import React from 'react';
import { Pagination as BootstrapPagination } from 'react-bootstrap';
import PropTypes from 'prop-types';

/**
 * Componente de paginación reutilizable
 */
const Pagination = ({ currentPage, totalPages, onPageChange, maxPagesToShow = 5 }) => {
  // No mostrar paginación si solo hay una página
  if (totalPages <= 1) return null;
  
  // Calcular rango de páginas a mostrar
  let startPage = Math.max(1, currentPage - Math.floor(maxPagesToShow / 2));
  let endPage = Math.min(totalPages, startPage + maxPagesToShow - 1);
  
  // Ajustar si estamos cerca del final
  if (endPage - startPage + 1 < maxPagesToShow) {
    startPage = Math.max(1, endPage - maxPagesToShow + 1);
  }
  
  // Crear array de páginas a mostrar
  const pages = [];
  for (let i = startPage; i <= endPage; i++) {
    pages.push(i);
  }
  
  return (
    <BootstrapPagination className="justify-content-center mt-4">
      {/* Botón para ir a la primera página */}
      <BootstrapPagination.First 
        onClick={() => onPageChange(1)} 
        disabled={currentPage === 1}
      />
      
      {/* Botón para ir a la página anterior */}
      <BootstrapPagination.Prev 
        onClick={() => onPageChange(currentPage - 1)} 
        disabled={currentPage === 1}
      />
      
      {/* Mostrar elipsis si no estamos en las primeras páginas */}
      {startPage > 1 && (
        <>
          <BootstrapPagination.Item onClick={() => onPageChange(1)}>1</BootstrapPagination.Item>
          {startPage > 2 && <BootstrapPagination.Ellipsis disabled />}
        </>
      )}
      
      {/* Mostrar páginas */}
      {pages.map(page => (
        <BootstrapPagination.Item
          key={page}
          active={page === currentPage}
          onClick={() => onPageChange(page)}
        >
          {page}
        </BootstrapPagination.Item>
      ))}
      
      {/* Mostrar elipsis si no estamos en las últimas páginas */}
      {endPage < totalPages && (
        <>
          {endPage < totalPages - 1 && <BootstrapPagination.Ellipsis disabled />}
          <BootstrapPagination.Item onClick={() => onPageChange(totalPages)}>
            {totalPages}
          </BootstrapPagination.Item>
        </>
      )}
      
      {/* Botón para ir a la página siguiente */}
      <BootstrapPagination.Next 
        onClick={() => onPageChange(currentPage + 1)} 
        disabled={currentPage === totalPages}
      />
      
      {/* Botón para ir a la última página */}
      <BootstrapPagination.Last 
        onClick={() => onPageChange(totalPages)} 
        disabled={currentPage === totalPages}
      />
    </BootstrapPagination>
  );
};

Pagination.propTypes = {
  currentPage: PropTypes.number.isRequired,
  totalPages: PropTypes.number.isRequired,
  onPageChange: PropTypes.func.isRequired,
  maxPagesToShow: PropTypes.number
};

export default Pagination;