import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card } from 'react-bootstrap';
import { Line, Bar } from 'react-chartjs-2';
import { Chart, registerables } from 'chart.js';
import { FaShoppingCart, FaUsers, FaBoxes, FaTools } from 'react-icons/fa';
import { ventasService, clientesService, inventarioService, reparacionesService } from '../../services/api';

// Registrar componentes de Chart.js
Chart.register(...registerables);

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({
    ventasMes: 0,
    totalClientes: 0,
    totalProductos: 0,
    reparacionesPendientes: 0,
    ventasMensuales: [],
    productosBajoStock: []
  });

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        
        // En un caso real, estas serían llamadas a la API
        // Aquí usamos datos de ejemplo para la demostración
        
        // Simular carga de datos
        await new Promise(resolve => setTimeout(resolve, 500));
        
        setStats({
          ventasMes: 40000,
          totalClientes: 215,
          totalProductos: 150,
          reparacionesPendientes: 18,
          ventasMensuales: [
            { mes: 'Ene', valor: 12000 },
            { mes: 'Feb', valor: 19000 },
            { mes: 'Mar', valor: 15000 },
            { mes: 'Abr', valor: 25000 },
            { mes: 'May', valor: 22000 },
            { mes: 'Jun', valor: 30000 },
            { mes: 'Jul', valor: 35000 },
            { mes: 'Ago', valor: 32000 },
            { mes: 'Sep', valor: 38000 },
            { mes: 'Oct', valor: 40000 },
            { mes: 'Nov', valor: 42000 },
            { mes: 'Dic', valor: 45000 }
          ],
          productosBajoStock: [
            { nombre: 'Producto 1', stock: 5, minimo: 10 },
            { nombre: 'Producto 2', stock: 3, minimo: 15 },
            { nombre: 'Producto 3', stock: 8, minimo: 10 },
            { nombre: 'Producto 4', stock: 2, minimo: 5 },
            { nombre: 'Producto 5', stock: 7, minimo: 20 }
          ]
        });
      } catch (err) {
        setError('Error al cargar los datos del dashboard');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  // Datos para el gráfico de ventas mensuales
  const ventasChartData = {
    labels: stats.ventasMensuales.map(item => item.mes),
    datasets: [
      {
        label: 'Ventas 2023',
        data: stats.ventasMensuales.map(item => item.valor),
        backgroundColor: 'rgba(78, 115, 223, 0.05)',
        borderColor: 'rgba(78, 115, 223, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(78, 115, 223, 1)',
        pointBorderColor: '#fff',
        pointHoverRadius: 3,
        pointHoverBackgroundColor: 'rgba(78, 115, 223, 1)',
        pointHoverBorderColor: 'rgba(78, 115, 223, 1)',
        pointHitRadius: 10,
        pointBorderWidth: 2,
        tension: 0.3,
        fill: true
      }
    ]
  };

  const ventasChartOptions = {
    maintainAspectRatio: false,
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function(value) {
            return '$' + value.toLocaleString();
          }
        }
      }
    },
    plugins: {
      legend: {
        display: false
      }
    }
  };

  if (loading) {
    return (
      <Container>
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Cargando...</span>
          </div>
          <p className="mt-3">Cargando datos del dashboard...</p>
        </div>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      </Container>
    );
  }

  return (
    <Container fluid>
      <h1 className="h3 mb-4">Dashboard</h1>
      
      {/* Tarjetas de resumen */}
      <Row className="mb-4">
        <Col md={3} className="mb-4">
          <Card className="border-left-primary h-100">
            <Card.Body>
              <Row className="align-items-center">
                <Col>
                  <div className="text-xs font-weight-bold text-primary text-uppercase mb-1">
                    Ventas (Mes)
                  </div>
                  <div className="h5 mb-0 font-weight-bold text-gray-800">
                    ${stats.ventasMes.toLocaleString()}
                  </div>
                </Col>
                <Col xs="auto">
                  <FaShoppingCart size={32} className="text-gray-300" />
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>

        <Col md={3} className="mb-4">
          <Card className="border-left-success h-100">
            <Card.Body>
              <Row className="align-items-center">
                <Col>
                  <div className="text-xs font-weight-bold text-success text-uppercase mb-1">
                    Clientes
                  </div>
                  <div className="h5 mb-0 font-weight-bold text-gray-800">
                    {stats.totalClientes}
                  </div>
                </Col>
                <Col xs="auto">
                  <FaUsers size={32} className="text-gray-300" />
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>

        <Col md={3} className="mb-4">
          <Card className="border-left-info h-100">
            <Card.Body>
              <Row className="align-items-center">
                <Col>
                  <div className="text-xs font-weight-bold text-info text-uppercase mb-1">
                    Productos
                  </div>
                  <div className="h5 mb-0 font-weight-bold text-gray-800">
                    {stats.totalProductos}
                  </div>
                </Col>
                <Col xs="auto">
                  <FaBoxes size={32} className="text-gray-300" />
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>

        <Col md={3} className="mb-4">
          <Card className="border-left-warning h-100">
            <Card.Body>
              <Row className="align-items-center">
                <Col>
                  <div className="text-xs font-weight-bold text-warning text-uppercase mb-1">
                    Reparaciones Pendientes
                  </div>
                  <div className="h5 mb-0 font-weight-bold text-gray-800">
                    {stats.reparacionesPendientes}
                  </div>
                </Col>
                <Col xs="auto">
                  <FaTools size={32} className="text-gray-300" />
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Gráficos y tablas */}
      <Row>
        <Col lg={8} className="mb-4">
          <Card className="shadow mb-4">
            <Card.Header className="py-3">
              <h6 className="m-0 font-weight-bold text-primary">Ventas Mensuales</h6>
            </Card.Header>
            <Card.Body>
              <div style={{ height: '300px' }}>
                <Line data={ventasChartData} options={ventasChartOptions} />
              </div>
            </Card.Body>
          </Card>
        </Col>

        <Col lg={4} className="mb-4">
          <Card className="shadow mb-4">
            <Card.Header className="py-3">
              <h6 className="m-0 font-weight-bold text-primary">Productos con Bajo Stock</h6>
            </Card.Header>
            <Card.Body>
              <div className="table-responsive">
                <table className="table table-sm">
                  <thead>
                    <tr>
                      <th>Producto</th>
                      <th>Stock</th>
                      <th>Mínimo</th>
                    </tr>
                  </thead>
                  <tbody>
                    {stats.productosBajoStock.map((producto, index) => (
                      <tr key={index}>
                        <td>{producto.nombre}</td>
                        <td>{producto.stock}</td>
                        <td>{producto.minimo}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="mt-3">
                <a href="/inventario/productos" className="btn btn-primary btn-sm">
                  Ver todos
                </a>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Dashboard;