import React, { useState } from 'react';
import axios from 'axios';
import './FlujoPedidos.css';

function FlujoPedidos() {
  const [fecha, setFecha] = useState('');
  const [reporte, setReporte] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const token = localStorage.getItem('token');
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      const response = await axios.get(`http://localhost:5000/pedidos/flujo/${fecha}`, { headers });
      setReporte(response.data);
    } catch (err) {
      setError('Error al obtener el reporte de pedidos');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flujo-pedidos">
      <h2>Análisis de Pedidos por Fecha</h2>
      
      <form onSubmit={handleSubmit} className="fecha-form">
        <div className="form-group">
          <label>Fecha de Entrega:</label>
          <input
            type="date"
            value={fecha}
            onChange={(e) => setFecha(e.target.value)}
            required
          />
        </div>
        <button type="submit" className="analyze-button">
          Analizar Pedidos
        </button>
      </form>

      {loading && <div className="loading">Cargando...</div>}
      {error && <div className="error">{error}</div>}

      {reporte && (
        <div className="reporte-container">
          <div className="reporte-header">
            <h3>Reporte de Pedidos - {new Date(reporte.fecha_entrega).toLocaleDateString()}</h3>
            <div className="resumen">
              <p>Total de Pedidos: {reporte.total_pedidos}</p>
              {reporte.tiene_problemas_stock && (
                <div className="alerta-stock">
                  ⚠️ Hay problemas de stock en algunos filamentos
                </div>
              )}
            </div>
          </div>

          {reporte.analisis_stock && (
            <div className="analisis-stock">
              <h4>Análisis de Stock</h4>
              
              {reporte.analisis_stock.problemas_stock.length > 0 ? (
                <div className="problemas-stock">
                  <h5>Problemas de Stock Detectados:</h5>
                  {reporte.analisis_stock.problemas_stock.map((problema, index) => (
                    <div key={index} className="problema-item">
                      <h6>{problema.nombre}</h6>
                      <p>Stock Actual: {problema.stock_actual}</p>
                      <p>Cantidad Necesaria: {problema.cantidad_necesaria}</p>
                      <p>Falta: {problema.diferencia}</p>
                      <div className="productos-afectados">
                        <h6>Productos Afectados:</h6>
                        <ul>
                          {problema.productos_afectados.map((producto, idx) => (
                            <li key={idx}>
                              {producto.nombre_producto} - Cantidad: {producto.cantidad}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="stock-ok">✅ No hay problemas de stock para esta fecha</p>
              )}

              <div className="filamentos-necesarios">
                <h5>Filamentos Necesarios:</h5>
                <div className="filamentos-grid">
                  {Object.entries(reporte.analisis_stock.filamentos_necesarios).map(([id, info]) => (
                    <div key={id} className="filamento-card">
                      <h6>{info.nombre}</h6>
                      <p>Stock Actual: {info.stock_actual}</p>
                      <p>Cantidad Necesaria: {info.cantidad_necesaria}</p>
                      <div className="productos">
                        <h6>Productos:</h6>
                        <ul>
                          {info.productos.map((producto, idx) => (
                            <li key={idx}>
                              {producto.nombre_producto} - Cantidad: {producto.cantidad}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          <div className="pedidos-lista">
            <h4>Pedidos para esta fecha:</h4>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>ID Pedido</th>
                    <th>Producto</th>
                    <th>Cantidad</th>
                    <th>Estado</th>
                  </tr>
                </thead>
                <tbody>
                  {reporte.pedidos.map(pedido => (
                    <tr key={pedido.id}>
                      <td>{pedido.id}</td>
                      <td>{pedido.producto}</td>
                      <td>{pedido.cantidad}</td>
                      <td>{pedido.estado}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default FlujoPedidos; 