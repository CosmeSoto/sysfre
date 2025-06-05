import React, { memo } from 'react';
import { Link } from 'react-router-dom';
import { Button } from 'react-bootstrap';
import AccessibleButton from './common/AccessibleButton';
import OptimizedImage from './common/OptimizedImage';

const ProductoItem = ({ producto, onEdit, onDelete }) => {
  return (
    <tr>
      <td>{producto.codigo}</td>
      <td>
        <Link to={`/inventario/productos/${producto.id}`}>
          {producto.nombre}
        </Link>
      </td>
      <td>
        {producto.imagen && (
          <OptimizedImage 
            src={producto.imagen} 
            alt={`Imagen de ${producto.nombre}`} 
            width="50" 
            height="50" 
            className="img-thumbnail"
          />
        )}
      </td>
      <td>{producto.precio_venta}</td>
      <td>{producto.stock}</td>
      <td>
        <AccessibleButton 
          variant="outline-primary" 
          size="sm" 
          onClick={() => onEdit(producto.id)}
          ariaLabel={`Editar ${producto.nombre}`}
          className="me-2"
        >
          Editar
        </AccessibleButton>
        <AccessibleButton 
          variant="outline-danger" 
          size="sm" 
          onClick={() => onDelete(producto.id)}
          ariaLabel={`Eliminar ${producto.nombre}`}
        >
          Eliminar
        </AccessibleButton>
      </td>
    </tr>
  );
};

// Solo re-renderizar si cambian las props
export default memo(ProductoItem);