import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './UserDashboard.css';

function UserDashboard() {
  const [activeTab, setActiveTab] = useState('productos');
  const [productos, setProductos] = useState([]);
  const [pedidos, setPedidos] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [categoriaSeleccionada, setCategoriaSeleccionada] = useState('todas');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [productoSeleccionado, setProductoSeleccionado] = useState(null);
  const [formData, setFormData] = useState({
    cantidad: 1,
    especificaciones: '',
    direccion_entrega: '',
    telefono: '',
    fecha_entrega: new Date().toISOString().split('T')[0],
    color_seleccionado: ''
  });

  useEffect(() => {
    fetchData();
  }, [activeTab]);

  const fetchData = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        window.location.href = '/login';
        return;
      }

      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      if (activeTab === 'productos') {
        const response = await axios.get('http://localhost:5000/productos', { headers });
        setProductos(response.data);

        // Obtener categorías
        const categoriasResponse = await axios.get('http://localhost:5000/categorias', { headers });
        setCategorias(categoriasResponse.data);
      } else {
        const response = await axios.get('http://localhost:5000/pedidos', { headers });
        setPedidos(response.data);
      }
      setLoading(false);
    } catch (err) {
      if (err.response && err.response.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('userRole');
        window.location.href = '/login';
      } else {
        setError('Error al cargar los datos');
      }
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handlePedido = (producto) => {
    setProductoSeleccionado(producto);
    setShowModal(true);
  };

  const handleSubmitPedido = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      const pedidoData = {
        producto_id: productoSeleccionado._id,
        cantidad: formData.cantidad,
        color_seleccionado: formData.color_seleccionado,
        especificaciones: formData.especificaciones,
        direccion_entrega: formData.direccion_entrega,
        telefono: formData.telefono,
        fecha_entrega: formData.fecha_entrega,
        estado: 'pendiente',
        fecha: new Date().toISOString()
      };

      await axios.post('http://localhost:5000/pedidos', pedidoData, { headers });
      
      setShowModal(false);
      setProductoSeleccionado(null);
      setFormData({
        cantidad: 1,
        especificaciones: '',
        direccion_entrega: '',
        telefono: '',
        fecha_entrega: new Date().toISOString().split('T')[0],
        color_seleccionado: ''
      });
      
      // Actualizar la lista de pedidos
      if (activeTab === 'pedidos') {
        fetchData();
      }
      
      alert('Pedido realizado con éxito');
    } catch (err) {
      if (err.response && err.response.data && err.response.data.error) {
        setError(err.response.data.error);
      } else {
        setError('Error al realizar el pedido');
      }
      console.error('Error completo:', err);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userRole');
    window.location.href = '/login';
  };

  const productosFiltrados = categoriaSeleccionada === 'todas' 
    ? productos 
    : productos.filter(p => p.categoria === categoriaSeleccionada);

  if (loading) return <div className="loading">Cargando...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="user-dashboard">
      <div className="dashboard-header">
        <h1>Panel de Usuario</h1>
        <button className="logout-button" onClick={handleLogout}>
          Cerrar Sesión
        </button>
      </div>

      <div className="tabs">
        <button 
          className={`tab-button ${activeTab === 'productos' ? 'active' : ''}`}
          onClick={() => setActiveTab('productos')}
        >
          Productos
        </button>
        <button 
          className={`tab-button ${activeTab === 'pedidos' ? 'active' : ''}`}
          onClick={() => setActiveTab('pedidos')}
        >
          Mis Pedidos
        </button>
      </div>

      {activeTab === 'productos' ? (
        <div className="productos-section">
          <div className="categorias-filter">
            <select 
              value={categoriaSeleccionada} 
              onChange={(e) => setCategoriaSeleccionada(e.target.value)}
            >
              <option value="todas">Todas las categorías</option>
              {categorias.map(categoria => (
                <option key={categoria._id} value={categoria.nombre}>
                  {categoria.nombre}
                </option>
              ))}
            </select>
          </div>

          <div className="productos-grid">
            {productosFiltrados.map(producto => (
              <div key={producto._id} className="producto-card">
                <h3>{producto.nombre}</h3>
                <p className="descripcion">{producto.descripcion}</p>
                <p className="precio">${producto.precio}</p>
                <p className="tiempo-entrega">Tiempo de entrega: {producto.tiempo_entrega}</p>
                <div className="materiales">
                  <strong>Materiales disponibles:</strong>
                  <ul>
                    {producto.materiales_disponibles?.map((material, index) => (
                      <li key={index}>{material}</li>
                    ))}
                  </ul>
                </div>
                <button 
                  className="pedir-button"
                  onClick={() => handlePedido(producto)}
                >
                  Realizar Pedido
                </button>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="pedidos-section">
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>ID Pedido</th>
                  <th>Producto</th>
                  <th>Cantidad</th>
                  <th>Dirección</th>
                  <th>Especificaciones</th>
                  <th>Estado</th>
                  <th>Fecha Creación</th>
                  <th>Fecha Entrega</th>
                </tr>
              </thead>
              <tbody>
                {pedidos.map(pedido => (
                  <tr key={pedido._id}>
                    <td>{pedido._id}</td>
                    <td>{pedido.producto?.nombre || 'Producto no disponible'}</td>
                    <td>{pedido.cantidad}</td>
                    <td>{pedido.direccion_entrega}</td>
                    <td>{pedido.especificaciones || 'Sin especificaciones'}</td>
                    <td>
                      <span className={`estado-badge ${pedido.estado}`}>
                        {pedido.estado === 'pendiente' ? 'Pendiente' :
                         pedido.estado === 'en_proceso' ? 'En Proceso' :
                         pedido.estado === 'enviado' ? 'Enviado' : pedido.estado}
                      </span>
                    </td>
                    <td>{new Date(pedido.fecha).toLocaleDateString()}</td>
                    <td>{new Date(pedido.fecha_entrega).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {showModal && productoSeleccionado && (
        <div className="modal">
          <div className="modal-content">
            <h2>Realizar Pedido - {productoSeleccionado.nombre}</h2>
            <form onSubmit={handleSubmitPedido}>
              <div className="form-group">
                <label>Cantidad:</label>
                <input
                  type="number"
                  name="cantidad"
                  value={formData.cantidad}
                  onChange={handleInputChange}
                  min="1"
                  required
                />
              </div>
              
              <div className="form-group">
                <label>Color del filamento:</label>
                <select
                  name="color_seleccionado"
                  value={formData.color_seleccionado}
                  onChange={handleInputChange}
                  required
                >
                  <option value="">Seleccione un color</option>
                  {productoSeleccionado.filamentos?.map((filamento, index) => (
                    <option key={index} value={filamento.color}>
                      {filamento.color} - {filamento.material}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Especificaciones adicionales:</label>
                <textarea
                  name="especificaciones"
                  value={formData.especificaciones}
                  onChange={handleInputChange}
                  placeholder="Detalles adicionales del pedido..."
                />
              </div>

              <div className="form-group">
                <label>Dirección de entrega:</label>
                <input
                  type="text"
                  name="direccion_entrega"
                  value={formData.direccion_entrega}
                  onChange={handleInputChange}
                  required
                  placeholder="Ingrese su dirección completa"
                />
              </div>

              <div className="form-group">
                <label>Teléfono de contacto:</label>
                <input
                  type="tel"
                  name="telefono"
                  value={formData.telefono}
                  onChange={handleInputChange}
                  required
                  placeholder="Ingrese su número de teléfono"
                  pattern="[0-9]{10}"
                  title="Ingrese un número de teléfono válido de 10 dígitos"
                />
              </div>

              <div className="form-group">
                <label>Fecha de entrega deseada:</label>
                <input
                  type="date"
                  name="fecha_entrega"
                  value={formData.fecha_entrega}
                  onChange={handleInputChange}
                  required
                  min={new Date().toISOString().split('T')[0]}
                />
              </div>

              <div className="modal-buttons">
                <button type="submit" className="submit-button">
                  Confirmar Pedido
                </button>
                <button 
                  type="button" 
                  className="cancel-button"
                  onClick={() => setShowModal(false)}
                >
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default UserDashboard; 