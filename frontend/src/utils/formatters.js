/**
 * Formatea un número como moneda
 * @param {number} value - Valor a formatear
 * @param {string} currency - Símbolo de moneda (por defecto: $)
 * @param {number} decimals - Número de decimales (por defecto: 2)
 * @returns {string} Valor formateado como moneda
 */
export const formatCurrency = (value, currency = '$', decimals = 2) => {
  if (value === null || value === undefined) return '';
  
  return `${currency}${parseFloat(value).toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;
};

/**
 * Formatea una fecha
 * @param {string|Date} date - Fecha a formatear
 * @param {object} options - Opciones de formato (por defecto: día/mes/año)
 * @returns {string} Fecha formateada
 */
export const formatDate = (date, options = {}) => {
  if (!date) return '';
  
  const defaultOptions = {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    ...options
  };
  
  return new Date(date).toLocaleDateString(undefined, defaultOptions);
};

/**
 * Formatea una fecha y hora
 * @param {string|Date} date - Fecha a formatear
 * @param {object} options - Opciones de formato
 * @returns {string} Fecha y hora formateadas
 */
export const formatDateTime = (date, options = {}) => {
  if (!date) return '';
  
  const defaultOptions = {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    ...options
  };
  
  return new Date(date).toLocaleString(undefined, defaultOptions);
};

/**
 * Trunca un texto si excede la longitud máxima
 * @param {string} text - Texto a truncar
 * @param {number} maxLength - Longitud máxima (por defecto: 50)
 * @returns {string} Texto truncado
 */
export const truncateText = (text, maxLength = 50) => {
  if (!text) return '';
  
  if (text.length <= maxLength) return text;
  
  return `${text.substring(0, maxLength)}...`;
};

/**
 * Formatea un número con separadores de miles
 * @param {number} value - Valor a formatear
 * @param {number} decimals - Número de decimales (por defecto: 0)
 * @returns {string} Número formateado
 */
export const formatNumber = (value, decimals = 0) => {
  if (value === null || value === undefined) return '';
  
  return parseFloat(value).toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
};

/**
 * Capitaliza la primera letra de cada palabra
 * @param {string} text - Texto a capitalizar
 * @returns {string} Texto capitalizado
 */
export const capitalizeText = (text) => {
  if (!text) return '';
  
  return text
    .toLowerCase()
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};