import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { inventarioService } from '../../services/api';

const ProductoList = () => {
  const [productos, setProductos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    categoria: '',
    estado: '',
    activo: true
  });

  useEffect(() => {
    fetchProductos();
  }, [currentPage, filters]);

  const fetchProductos = async () => {
    setLoading(true);
    try {
      const params = {
        page: currentPage,
        search: searchTerm,
        ...filters
      };
      
      const response = await inventarioService.getProductos(params);
      setProductos(response.data.results);
      setTotalPages(Math.ceil(response.data.count / 10));
    } catch (err) {
      setError('Error al cargar los productos');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    fetchProductos();
  };

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
    setCurrentPage(1);
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Productos</h1>
        <Link
          to="/inventario/productos/nuevo"
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          Nuevo Producto
        </Link>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="mb-6">
        <form onSubmit={handleSearch} className="flex gap-4">
          <input
            type="text"
            placeholder="Buscar productos..."
            className="border rounded px-3 py-2 w-full"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <button
            type="submit"
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
          >
            Buscar
          </button>
        </form>
      </div>

      <div className="mb-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Categoría
          </label>
          <select
            name="categoria"
            value={filters.categoria}
            onChange={handleFilterChange}
            className="border rounded px-3 py-2 w-full"
          >
            <option value="">Todas</option>
            {/* Aquí se cargarían dinámicamente las categorías */}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Estado
          </label>
          <select
            name="estado"
            value={filters.estado}
            onChange={handleFilterChange}
            className="border rounded px-3 py-2 w-full"
          >
            <option value="">Todos</option>
            <option value="disponible">Disponible</option>
            <option value="agotado">Agotado</option>
            <option value="descontinuado">Descontinuado</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Activo
          </label>
          <select
            name="activo"
            value={filters.activo}
            onChange={handleFilterChange}
            className="border rounded px-3 py-2 w-full"
          >
            <option value="true">Sí</option>
            <option value="false">No</option>
            <option value="">Todos</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-8">Cargando productos...</div>
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="min-w-full bg-white border">
              <thead>
                <tr>
                  <th className="py-2 px-4 border-b">Código</th>
                  <th className="py-2 px-4 border-b">Nombre</th>
                  <th className="py-2 px-4 border-b">Categoría</th>
                  <th className="py-2 px-4 border-b">Stock</th>
                  <th className="py-2 px-4 border-b">Precio Venta</th>
                  <th className="py-2 px-4 border-b">Estado</th>
                  <th className="py-2 px-4 border-b">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {productos.length > 0 ? (
                  productos.map((producto) => (
                    <tr key={producto.id}>
                      <td className="py-2 px-4 border-b">{producto.codigo}</td>
                      <td className="py-2 px-4 border-b">{producto.nombre}</td>
                      <td className="py-2 px-4 border-b">{producto.categoria_nombre}</td>
                      <td className="py-2 px-4 border-b">
                        {producto.stock}
                        {producto.stock <= producto.stock_minimo && (
                          <span className="ml-2 text-red-500 text-xs">Bajo</span>
                        )}
                      </td>
                      <td className="py-2 px-4 border-b">${producto.precio_venta.toFixed(2)}</td>
                      <td className="py-2 px-4 border-b">
                        <span
                          className={`px-2 py-1 rounded text-xs ${
                            producto.estado === 'disponible'
                              ? 'bg-green-100 text-green-800'
                              : producto.estado === 'agotado'
                              ? 'bg-red-100 text-red-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          {producto.estado}
                        </span>
                      </td>
                      <td className="py-2 px-4 border-b">
                        <div className="flex space-x-2">
                          <Link
                            to={`/inventario/productos/${producto.id}`}
                            className="text-blue-500 hover:text-blue-700"
                          >
                            Ver
                          </Link>
                          <Link
                            to={`/inventario/productos/${producto.id}/editar`}
                            className="text-yellow-500 hover:text-yellow-700"
                          >
                            Editar
                          </Link>
                        </div>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="7" className="py-4 text-center">
                      No se encontraron productos
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {totalPages > 1 && (
            <div className="flex justify-center mt-6">
              <nav>
                <ul className="flex space-x-2">
                  {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                    <li key={page}>
                      <button
                        onClick={() => handlePageChange(page)}
                        className={`px-3 py-1 rounded ${
                          currentPage === page
                            ? 'bg-blue-500 text-white'
                            : 'bg-gray-200 hover:bg-gray-300'
                        }`}
                      >
                        {page}
                      </button>
                    </li>
                  ))}
                </ul>
              </nav>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default ProductoList;