import React from 'react';

const OptimizedImage = ({ src, alt, width, height, className }) => {
  return (
    <img 
      src={src} 
      alt={alt} 
      width={width} 
      height={height} 
      className={className}
      loading="lazy" // Carga diferida de imágenes
    />
  );
};

export default OptimizedImage;