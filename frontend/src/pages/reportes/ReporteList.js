import React, { useState } from 'react';
import { Container, Card, Row, Col, Form, Button, Table } from 'react-bootstrap';
import { FaFileAlt, FaFileExcel, FaFilePdf, FaChartBar } from 'react-icons/fa';
import { reportesService } from '../../services/api';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import ErrorMessage from '../../components/common/ErrorMessage';
import { toast } from 'react-toastify';

const ReporteList = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [reporteSeleccionado, setReporteSeleccionado] = useState('');
  const [fechaInicio, setFechaInicio] = useState('');
  const [fechaFin, setFechaFin] = useState('');
  const [formato, setFormato] = useState('pdf');
  const [parametrosAdicionales, setParametrosAdicionales] = useState({});

  // Lista de reportes disponibles
  const reportes = [
    { id: 'ventas_diarias', nombre: 'Ventas Diarias', categoria: 'ventas' },
    { id: 'ventas_mensuales', nombre: 'Ventas Mensuales', categoria: 'ventas' },
    { id: 'ventas_por_cliente', nombre: 'Ventas por Cliente', categoria: 'ventas' },
    { id: 'ventas_por_producto', nombre: 'Ventas por Producto', categoria: 'ventas' },
    { id: 'inventario_actual', nombre: 'Inventario Actual', categoria: 'inventario' },
    { id: 'productos_bajo_stock', nombre: 'Productos con Bajo Stock', categoria: 'inventario' },
    { id: 'movimientos_inventario', nombre: 'Movimientos de Inventario', categoria: 'inventario' },
    { id: 'reparaciones_pendientes', nombre: 'Reparaciones Pendientes', categoria: 'reparaciones' },
    { id: 'reparaciones_por_tecnico', nombre: 'Reparaciones por Técnico', categoria: 'reparaciones' },
    { id: 'balance_general', nombre: 'Balance General', categoria: 'contabilidad' },
    { id: 'estado_resultados', nombre: 'Estado de Resultados', categoria: 'contabilidad' },
    { id: 'libro_diario', nombre: 'Libro Diario', categoria: 'contabilidad' },
    { id: 'libro_mayor', nombre: 'Libro Mayor', categoria: 'contabilidad' }
  ];

  // Agrupar reportes por categoría
  const reportesPorCategoria = reportes.reduce((acc, reporte) => {
    if (!acc[reporte.categoria]) {
      acc[reporte.categoria] = [];
    }
    acc[reporte.categoria].push(reporte);
    return acc;
  }, {});

  // Manejar cambio de reporte
  const handleReporteChange = (e) => {
    setReporteSeleccionado(e.target.value);
    setParametrosAdicionales({});
  };

  // Manejar cambio de parámetros adicionales
  const handleParametroChange = (e) => {
    const { name, value } = e.target;
    setParametrosAdicionales(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Generar reporte
  const handleGenerarReporte = async () => {
    if (!reporteSeleccionado) {
      toast.error('Debe seleccionar un reporte');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const params = {
        reporte: reporteSeleccionado,
        formato,
        fecha_inicio: fechaInicio || undefined,
        fecha_fin: fechaFin || undefined,
        ...parametrosAdicionales
      };
      
      const response = await reportesService.generarReporte(params);
      
      // Descargar archivo
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${reporteSeleccionado}.${formato}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast.success('Reporte generado correctamente');
    } catch (err) {
      setError('Error al generar el reporte');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Renderizar parámetros adicionales según el reporte seleccionado
  const renderParametrosAdicionales = () => {
    switch (reporteSeleccionado) {
      case 'ventas_por_cliente':
        return (
          <Form.Group className="mb-3">
            <Form.Label>Cliente</Form.Label>
            <Form.Select
              name="cliente_id"
              value={parametrosAdicionales.cliente_id || ''}
              onChange={handleParametroChange}
            >
              <option value="">Todos los clientes</option>
              <option value="1">Cliente 1</option>
              <option value="2">Cliente 2</option>
              <option value="3">Cliente 3</option>
            </Form.Select>
          </Form.Group>
        );
      
      case 'ventas_por_producto':
        return (
          <Form.Group className="mb-3">
            <Form.Label>Categoría de Producto</Form.Label>
            <Form.Select
              name="categoria_id"
              value={parametrosAdicionales.categoria_id || ''}
              onChange={handleParametroChange}
            >
              <option value="">Todas las categorías</option>
              <option value="1">Categoría 1</option>
              <option value="2">Categoría 2</option>
              <option value="3">Categoría 3</option>
            </Form.Select>
          </Form.Group>
        );
      
      case 'movimientos_inventario':
        return (
          <Form.Group className="mb-3">
            <Form.Label>Tipo de Movimiento</Form.Label>
            <Form.Select
              name="tipo_movimiento"
              value={parametrosAdicionales.tipo_movimiento || ''}
              onChange={handleParametroChange}
            >
              <option value="">Todos</option>
              <option value="entrada">Entradas</option>
              <option value="salida">Salidas</option>
            </Form.Select>
          </Form.Group>
        );
      
      case 'reparaciones_por_tecnico':
        return (
          <Form.Group className="mb-3">
            <Form.Label>Técnico</Form.Label>
            <Form.Select
              name="tecnico_id"
              value={parametrosAdicionales.tecnico_id || ''}
              onChange={handleParametroChange}
            >
              <option value="">Todos los técnicos</option>
              <option value="1">Técnico 1</option>
              <option value="2">Técnico 2</option>
              <option value="3">Técnico 3</option>
            </Form.Select>
          </Form.Group>
        );
      
      case 'libro_mayor':
        return (
          <Form.Group className="mb-3">
            <Form.Label>Cuenta</Form.Label>
            <Form.Select
              name="cuenta_id"
              value={parametrosAdicionales.cuenta_id || ''}
              onChange={handleParametroChange}
            >
              <option value="">Todas las cuentas</option>
              <option value="1">Cuenta 1</option>
              <option value="2">Cuenta 2</option>
              <option value="3">Cuenta 3</option>
            </Form.Select>
          </Form.Group>
        );
      
      default:
        return null;
    }
  };

  return (
    <Container fluid>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 className="h3">Reportes</h1>
      </div>

      <ErrorMessage error={error} />

      <Row>
        <Col lg={4} className="mb-4">
          <Card>
            <Card.Header>
              <h5 className="card-title mb-0">Reportes Disponibles</h5>
            </Card.Header>
            <Card.Body>
              <Form.Group className="mb-3">
                <Form.Label>Seleccione un Reporte</Form.Label>
                <Form.Select
                  value={reporteSeleccionado}
                  onChange={handleReporteChange}
                >
                  <option value="">Seleccione un reporte</option>
                  {Object.entries(reportesPorCategoria).map(([categoria, reportes]) => (
                    <optgroup key={categoria} label={categoria.charAt(0).toUpperCase() + categoria.slice(1)}>
                      {reportes.map(reporte => (
                        <option key={reporte.id} value={reporte.id}>
                          {reporte.nombre}
                        </option>
                      ))}
                    </optgroup>
                  ))}
                </Form.Select>
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>Formato</Form.Label>
                <div>
                  <Form.Check
                    inline
                    type="radio"
                    label="PDF"
                    name="formato"
                    id="formato-pdf"
                    value="pdf"
                    checked={formato === 'pdf'}
                    onChange={() => setFormato('pdf')}
                  />
                  <Form.Check
                    inline
                    type="radio"
                    label="Excel"
                    name="formato"
                    id="formato-excel"
                    value="xlsx"
                    checked={formato === 'xlsx'}
                    onChange={() => setFormato('xlsx')}
                  />
                  <Form.Check
                    inline
                    type="radio"
                    label="CSV"
                    name="formato"
                    id="formato-csv"
                    value="csv"
                    checked={formato === 'csv'}
                    onChange={() => setFormato('csv')}
                  />
                </div>
              </Form.Group>
            </Card.Body>
          </Card>
        </Col>

        <Col lg={8} className="mb-4">
          <Card>
            <Card.Header>
              <h5 className="card-title mb-0">Parámetros del Reporte</h5>
            </Card.Header>
            <Card.Body>
              <Row className="mb-3">
                <Col md={6}>
                  <Form.Group>
                    <Form.Label>Fecha Inicio</Form.Label>
                    <Form.Control
                      type="date"
                      value={fechaInicio}
                      onChange={(e) => setFechaInicio(e.target.value)}
                    />
                  </Form.Group>
                </Col>
                <Col md={6}>
                  <Form.Group>
                    <Form.Label>Fecha Fin</Form.Label>
                    <Form.Control
                      type="date"
                      value={fechaFin}
                      onChange={(e) => setFechaFin(e.target.value)}
                    />
                  </Form.Group>
                </Col>
              </Row>

              {renderParametrosAdicionales()}

              <div className="d-grid gap-2 mt-4">
                <Button 
                  variant="primary" 
                  onClick={handleGenerarReporte}
                  disabled={loading || !reporteSeleccionado}
                >
                  {loading ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                      Generando...
                    </>
                  ) : (
                    <>
                      <FaFileAlt className="me-2" /> Generar Reporte
                    </>
                  )}
                </Button>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Card>
        <Card.Header>
          <h5 className="card-title mb-0">Reportes Recientes</h5>
        </Card.Header>
        <Card.Body>
          <Table striped hover responsive>
            <thead>
              <tr>
                <th>Reporte</th>
                <th>Fecha</th>
                <th>Usuario</th>
                <th>Formato</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Ventas Diarias</td>
                <td>2023-06-15 14:30</td>
                <td>admin@example.com</td>
                <td>PDF</td>
                <td>
                  <Button variant="outline-primary" size="sm" className="me-1">
                    <FaFilePdf />
                  </Button>
                </td>
              </tr>
              <tr>
                <td>Inventario Actual</td>
                <td>2023-06-14 10:15</td>
                <td>admin@example.com</td>
                <td>Excel</td>
                <td>
                  <Button variant="outline-success" size="sm" className="me-1">
                    <FaFileExcel />
                  </Button>
                </td>
              </tr>
              <tr>
                <td>Ventas Mensuales</td>
                <td>2023-06-10 09:45</td>
                <td>admin@example.com</td>
                <td>PDF</td>
                <td>
                  <Button variant="outline-primary" size="sm" className="me-1">
                    <FaFilePdf />
                  </Button>
                  <Button variant="outline-info" size="sm">
                    <FaChartBar />
                  </Button>
                </td>
              </tr>
            </tbody>
          </Table>
        </Card.Body>
      </Card>
    </Container>
  );
};

export default ReporteList;