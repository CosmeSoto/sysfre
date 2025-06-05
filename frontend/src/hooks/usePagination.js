import { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';

/**
 * Hook para manejar paginación
 * @param {Function} fetchData - Función para cargar datos
 * @param {Object} initialFilters - Filtros iniciales
 * @returns {Object} Estado y funciones para manejar paginación
 */
function usePagination(fetchData, initialFilters = {}) {
  const [searchParams, setSearchParams] = useSearchParams();
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [totalItems, setTotalItems] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  
  // Obtener página actual de los parámetros de URL o usar 1 por defecto
  const currentPage = parseInt(searchParams.get('page') || '1', 10);
  
  // Obtener filtros de los parámetros de URL
  const filters = { ...initialFilters };
  for (const [key, value] of searchParams.entries()) {
    if (key !== 'page') {
      filters[key] = value;
    }
  }

  // Función para cargar datos con paginación
  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = {
        page: currentPage,
        ...filters
      };
      
      const response = await fetchData(params);
      
      setData(response.data.results);
      setTotalItems(response.data.count);
      setTotalPages(Math.ceil(response.data.count / (response.data.page_size || 10)));
    } catch (err) {
      setError('Error al cargar los datos');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [fetchData, currentPage, filters]);

  // Cargar datos cuando cambia la página o los filtros
  useEffect(() => {
    loadData();
  }, [loadData]);

  // Función para cambiar de página
  const goToPage = (page) => {
    // Actualizar parámetros de URL
    const newParams = new URLSearchParams(searchParams);
    newParams.set('page', page.toString());
    setSearchParams(newParams);
  };

  // Función para aplicar filtros
  const applyFilters = (newFilters) => {
    // Actualizar parámetros de URL
    const newParams = new URLSearchParams();
    
    // Agregar filtros
    for (const [key, value] of Object.entries({ ...filters, ...newFilters })) {
      if (value) {
        newParams.set(key, value.toString());
      }
    }
    
    // Resetear página a 1 al aplicar filtros
    newParams.set('page', '1');
    
    setSearchParams(newParams);
  };

  // Función para limpiar filtros
  const clearFilters = () => {
    // Mantener solo el parámetro de página
    const newParams = new URLSearchParams();
    newParams.set('page', '1');
    setSearchParams(newParams);
  };

  return {
    data,
    loading,
    error,
    currentPage,
    totalPages,
    totalItems,
    filters,
    goToPage,
    applyFilters,
    clearFilters,
    refresh: loadData
  };
}

export default usePagination;