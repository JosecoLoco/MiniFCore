import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './AdminDashboard.css';

function AdminDashboard() {
  const [activeTab, setActiveTab] = useState('productos');
  const [productos, setProductos] = useState([]);
  const [pedidos, setPedidos] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [filamentos, setFilamentos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [showCategoriaModal, setShowCategoriaModal] = useState(false);
  const [showFilamentoModal, setShowFilamentoModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [editingCategoria, setEditingCategoria] = useState(null);
  const [editingFilamento, setEditingFilamento] = useState(null);
  const [formData, setFormData] = useState({
    nombre: '',
    descripcion: '',
    precio: '',
    categoria: '',
    stock: '',
    tiempo_entrega: '',
    filamentos: [],
    tamaño_maximo: ''
  });
  const [categoriaFormData, setCategoriaFormData] = useState({
    nombre: '',
    descripcion: ''
  });
  const [filamentoFormData, setFilamentoFormData] = useState({
    nombre: '',
    descripcion: '',
    color: '',
    material: '',
    diametro: '',
    stock: ''
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
        const [productosResponse, categoriasResponse, filamentosResponse] = await Promise.all([
          axios.get('http://localhost:5000/productos', { headers }),
          axios.get('http://localhost:5000/categorias', { headers }),
          axios.get('http://localhost:5000/filamentos', { headers })
        ]);
        setProductos(productosResponse.data);
        setCategorias(categoriasResponse.data);
        setFilamentos(filamentosResponse.data);
      } else if (activeTab === 'pedidos') {
        const response = await axios.get('http://localhost:5000/pedidos', { headers });
        setPedidos(response.data);
      } else if (activeTab === 'categorias') {
        const response = await axios.get('http://localhost:5000/categorias', { headers });
        setCategorias(response.data);
      } else if (activeTab === 'filamentos') {
        const response = await axios.get('http://localhost:5000/filamentos', { headers });
        setFilamentos(response.data);
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

  const handleCategoriaInputChange = (e) => {
    const { name, value } = e.target;
    setCategoriaFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleFilamentoInputChange = (e) => {
    const { name, value } = e.target;
    setFilamentoFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      if (editingProduct) {
        await axios.put(`http://localhost:5000/productos/${editingProduct._id}`, formData, { headers });
      } else {
        await axios.post('http://localhost:5000/productos', formData, { headers });
      }

      setShowModal(false);
      setEditingProduct(null);
      setFormData({
        nombre: '',
        descripcion: '',
        precio: '',
        categoria: '',
        stock: '',
        tiempo_entrega: '',
        filamentos: [],
        tamaño_maximo: ''
      });
      fetchData();
    } catch (err) {
      setError('Error al guardar el producto');
    }
  };

  const handleSubmitCategoria = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      if (editingCategoria) {
        await axios.put(`http://localhost:5000/categorias/${editingCategoria._id}`, categoriaFormData, { headers });
      } else {
        await axios.post('http://localhost:5000/categorias', categoriaFormData, { headers });
      }

      setShowCategoriaModal(false);
      setEditingCategoria(null);
      setCategoriaFormData({
        nombre: '',
        descripcion: ''
      });
      fetchData();
    } catch (err) {
      setError('Error al guardar la categoría');
    }
  };

  const handleSubmitFilamento = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      if (editingFilamento) {
        await axios.put(`http://localhost:5000/filamentos/${editingFilamento._id}`, filamentoFormData, { headers });
      } else {
        await axios.post('http://localhost:5000/filamentos', filamentoFormData, { headers });
      }

      setShowFilamentoModal(false);
      setEditingFilamento(null);
      setFilamentoFormData({
        nombre: '',
        descripcion: '',
        color: '',
        material: '',
        diametro: '',
        stock: ''
      });
      fetchData();
    } catch (err) {
      setError('Error al guardar el filamento');
    }
  };

  const handleEdit = (producto) => {
    setEditingProduct(producto);
    setFormData({
      nombre: producto.nombre,
      descripcion: producto.descripcion,
      precio: producto.precio,
      categoria: producto.categoria,
      stock: producto.stock,
      tiempo_entrega: producto.tiempo_entrega,
      filamentos: producto.filamentos?.map(f => f.nombre) || [],
      tamaño_maximo: producto.tamaño_maximo || ''
    });
    setShowModal(true);
  };

  const handleEditCategoria = (categoria) => {
    setEditingCategoria(categoria);
    setCategoriaFormData({
      nombre: categoria.nombre,
      descripcion: categoria.descripcion
    });
    setShowCategoriaModal(true);
  };

  const handleEditFilamento = (filamento) => {
    setEditingFilamento(filamento);
    setFilamentoFormData({
      nombre: filamento.nombre,
      descripcion: filamento.descripcion,
      color: filamento.color,
      material: filamento.material,
      diametro: filamento.diametro,
      stock: filamento.stock
    });
    setShowFilamentoModal(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('¿Estás seguro de que deseas eliminar este producto?')) {
      try {
        const token = localStorage.getItem('token');
        await axios.delete(`http://localhost:5000/productos/${id}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        fetchData();
      } catch (err) {
        setError('Error al eliminar el producto');
      }
    }
  };

  const handleDeleteCategoria = async (id) => {
    if (window.confirm('¿Estás seguro de que deseas eliminar esta categoría?')) {
      try {
        const token = localStorage.getItem('token');
        await axios.delete(`http://localhost:5000/categorias/${id}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        fetchData();
      } catch (err) {
        setError('Error al eliminar la categoría');
      }
    }
  };

  const handleDeleteFilamento = async (id) => {
    if (window.confirm('¿Estás seguro de que deseas eliminar este filamento?')) {
      try {
        const token = localStorage.getItem('token');
        await axios.delete(`http://localhost:5000/filamentos/${id}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        fetchData();
      } catch (err) {
        setError('Error al eliminar el filamento');
      }
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userRole');
    window.location.href = '/login';
  };

  const handleUpdateEstado = async (pedidoId, nuevoEstado) => {
    try {
      const token = localStorage.getItem('token');
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      await axios.put(`http://localhost:5000/pedidos/${pedidoId}/estado`, 
        { estado: nuevoEstado },
        { headers }
      );

      fetchData();
    } catch (err) {
      setError('Error al actualizar el estado del pedido');
    }
  };

  if (loading) return <div className="loading">Cargando...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="admin-dashboard">
      <div className="dashboard-header">
        <h1>Panel de Administración</h1>
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
          Pedidos
        </button>
        <button 
          className={`tab-button ${activeTab === 'categorias' ? 'active' : ''}`}
          onClick={() => setActiveTab('categorias')}
        >
          Categorías
        </button>
        <button 
          className={`tab-button ${activeTab === 'filamentos' ? 'active' : ''}`}
          onClick={() => setActiveTab('filamentos')}
        >
          Filamentos
        </button>
      </div>

      {activeTab === 'productos' ? (
        <div className="productos-section">
          <button className="add-button" onClick={() => setShowModal(true)}>
            Agregar Nuevo Producto
          </button>
          
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>Descripción</th>
                  <th>Precio</th>
                  <th>Categoría</th>
                  <th>Stock</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {productos.map(producto => (
                  <tr key={producto._id}>
                    <td>{producto.nombre}</td>
                    <td>{producto.descripcion}</td>
                    <td>${producto.precio}</td>
                    <td>{producto.categoria}</td>
                    <td>{producto.stock}</td>
                    <td>
                      <button
                        className="edit-button"
                        onClick={() => handleEdit(producto)}
                      >
                        Editar
                      </button>
                      <button
                        className="delete-button"
                        onClick={() => handleDelete(producto._id)}
                      >
                        Eliminar
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : activeTab === 'pedidos' ? (
        <div className="pedidos-section">
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>ID Pedido</th>
                  <th>Producto</th>
                  <th>Cantidad</th>
                  <th>Cliente</th>
                  <th>Teléfono</th>
                  <th>Dirección</th>
                  <th>Especificaciones</th>
                  <th>Estado</th>
                  <th>Fecha</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {pedidos.map(pedido => (
                  <tr key={pedido._id}>
                    <td>{pedido._id}</td>
                    <td>{pedido.producto?.nombre || 'Producto no disponible'}</td>
                    <td>{pedido.cantidad}</td>
                    <td>{pedido.cliente?.nombre || 'Cliente no disponible'}</td>
                    <td>{pedido.telefono}</td>
                    <td>{pedido.direccion_entrega}</td>
                    <td>{pedido.especificaciones || 'Sin especificaciones'}</td>
                    <td>
                      <select
                        value={pedido.estado}
                        onChange={(e) => handleUpdateEstado(pedido._id, e.target.value)}
                        className={`estado-select ${pedido.estado}`}
                      >
                        <option value="pendiente">Pendiente</option>
                        <option value="en_proceso">En Proceso</option>
                        <option value="enviado">Enviado</option>
                      </select>
                    </td>
                    <td>{new Date(pedido.fecha).toLocaleDateString()}</td>
                    <td>
                      <button
                        className="view-button"
                        onClick={() => {
                          alert(`Detalles del pedido:\n
                            Cliente: ${pedido.cliente?.nombre}\n
                            Teléfono: ${pedido.telefono}\n
                            Dirección: ${pedido.direccion_entrega}\n
                            Especificaciones: ${pedido.especificaciones || 'Sin especificaciones'}`
                          );
                        }}
                      >
                        Ver Detalles
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : activeTab === 'categorias' ? (
        <div className="categorias-section">
          <button className="add-button" onClick={() => setShowCategoriaModal(true)}>
            Agregar Nueva Categoría
          </button>
          
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>Descripción</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {categorias.map(categoria => (
                  <tr key={categoria._id}>
                    <td>{categoria.nombre}</td>
                    <td>{categoria.descripcion}</td>
                    <td>
                      <button
                        className="edit-button"
                        onClick={() => handleEditCategoria(categoria)}
                      >
                        Editar
                      </button>
                      <button
                        className="delete-button"
                        onClick={() => handleDeleteCategoria(categoria._id)}
                      >
                        Eliminar
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="filamentos-section">
          <button className="add-button" onClick={() => setShowFilamentoModal(true)}>
            Agregar Nuevo Filamento
          </button>
          
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>Descripción</th>
                  <th>Color</th>
                  <th>Material</th>
                  <th>Diámetro</th>
                  <th>Stock</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {filamentos.map(filamento => (
                  <tr key={filamento._id}>
                    <td>{filamento.nombre}</td>
                    <td>{filamento.descripcion}</td>
                    <td>{filamento.color}</td>
                    <td>{filamento.material}</td>
                    <td>{filamento.diametro}</td>
                    <td>{filamento.stock}</td>
                    <td>
                      <button
                        className="edit-button"
                        onClick={() => handleEditFilamento(filamento)}
                      >
                        Editar
                      </button>
                      <button
                        className="delete-button"
                        onClick={() => handleDeleteFilamento(filamento._id)}
                      >
                        Eliminar
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {showModal && (
        <div className="modal">
          <div className="modal-content">
            <h2>{editingProduct ? 'Editar Producto' : 'Nuevo Producto'}</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Nombre:</label>
                <input
                  type="text"
                  name="nombre"
                  value={formData.nombre}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="form-group">
                <label>Descripción:</label>
                <textarea
                  name="descripcion"
                  value={formData.descripcion}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="form-group">
                <label>Precio:</label>
                <input
                  type="number"
                  name="precio"
                  value={formData.precio}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="form-group">
                <label>Categoría:</label>
                <select
                  name="categoria"
                  value={formData.categoria}
                  onChange={handleInputChange}
                  required
                >
                  <option value="">Seleccionar categoría</option>
                  {categorias.map(categoria => (
                    <option key={categoria._id} value={categoria.nombre}>
                      {categoria.nombre}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Stock:</label>
                <input
                  type="number"
                  name="stock"
                  value={formData.stock}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="form-group">
                <label>Tiempo de Entrega:</label>
                <input
                  type="text"
                  name="tiempo_entrega"
                  value={formData.tiempo_entrega}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="form-group">
                <label>Filamentos:</label>
                <input
                  type="text"
                  name="filamentos"
                  value={formData.filamentos.join(', ')}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    filamentos: e.target.value.split(',').map(f => f.trim())
                  }))}
                  placeholder="Separados por comas"
                />
              </div>
              <div className="form-group">
                <label>Tamaño Máximo:</label>
                <input
                  type="text"
                  name="tamaño_maximo"
                  value={formData.tamaño_maximo}
                  onChange={handleInputChange}
                />
              </div>
              <div className="modal-buttons">
                <button type="submit" className="save-button">
                  {editingProduct ? 'Guardar Cambios' : 'Crear Producto'}
                </button>
                <button
                  type="button"
                  className="cancel-button"
                  onClick={() => {
                    setShowModal(false);
                    setEditingProduct(null);
                  }}
                >
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showCategoriaModal && (
        <div className="modal">
          <div className="modal-content">
            <h2>{editingCategoria ? 'Editar Categoría' : 'Nueva Categoría'}</h2>
            <form onSubmit={handleSubmitCategoria}>
              <div className="form-group">
                <label>Nombre:</label>
                <input
                  type="text"
                  name="nombre"
                  value={categoriaFormData.nombre}
                  onChange={handleCategoriaInputChange}
                  required
                />
              </div>
              <div className="form-group">
                <label>Descripción:</label>
                <textarea
                  name="descripcion"
                  value={categoriaFormData.descripcion}
                  onChange={handleCategoriaInputChange}
                  required
                />
              </div>
              <div className="modal-buttons">
                <button type="submit" className="save-button">
                  {editingCategoria ? 'Guardar Cambios' : 'Crear Categoría'}
                </button>
                <button
                  type="button"
                  className="cancel-button"
                  onClick={() => {
                    setShowCategoriaModal(false);
                    setEditingCategoria(null);
                  }}
                >
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showFilamentoModal && (
        <div className="modal">
          <div className="modal-content">
            <h2>{editingFilamento ? 'Editar Filamento' : 'Nuevo Filamento'}</h2>
            <form onSubmit={handleSubmitFilamento}>
              <div className="form-group">
                <label>Nombre:</label>
                <input
                  type="text"
                  name="nombre"
                  value={filamentoFormData.nombre}
                  onChange={handleFilamentoInputChange}
                  required
                />
              </div>
              <div className="form-group">
                <label>Descripción:</label>
                <textarea
                  name="descripcion"
                  value={filamentoFormData.descripcion}
                  onChange={handleFilamentoInputChange}
                  required
                />
              </div>
              <div className="form-group">
                <label>Color:</label>
                <input
                  type="text"
                  name="color"
                  value={filamentoFormData.color}
                  onChange={handleFilamentoInputChange}
                  required
                />
              </div>
              <div className="form-group">
                <label>Material:</label>
                <input
                  type="text"
                  name="material"
                  value={filamentoFormData.material}
                  onChange={handleFilamentoInputChange}
                  required
                />
              </div>
              <div className="form-group">
                <label>Diámetro:</label>
                <input
                  type="text"
                  name="diametro"
                  value={filamentoFormData.diametro}
                  onChange={handleFilamentoInputChange}
                  required
                />
              </div>
              <div className="form-group">
                <label>Stock:</label>
                <input
                  type="number"
                  name="stock"
                  value={filamentoFormData.stock}
                  onChange={handleFilamentoInputChange}
                  required
                />
              </div>
              <div className="modal-buttons">
                <button type="submit" className="save-button">
                  {editingFilamento ? 'Guardar Cambios' : 'Crear Filamento'}
                </button>
                <button
                  type="button"
                  className="cancel-button"
                  onClick={() => {
                    setShowFilamentoModal(false);
                    setEditingFilamento(null);
                  }}
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

export default AdminDashboard; 