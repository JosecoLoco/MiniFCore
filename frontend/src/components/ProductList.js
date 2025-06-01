import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './ProductList.css';

function ProductList() {
  const [productos, setProductos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProductos = async () => {
      try {
        const response = await axios.get('http://localhost:5000/productos');
        setProductos(response.data);
        setLoading(false);
      } catch (err) {
        setError('Error al cargar los productos');
        setLoading(false);
      }
    };

    fetchProductos();
  }, []);

  if (loading) return <div className="loading">Cargando productos...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="product-list">
      <h2>Nuestros Servicios y Productos</h2>
      <div className="product-grid">
        {productos.map((producto) => (
          <div key={producto._id} className="product-card">
            <h3>{producto.nombre}</h3>
            <p className="description">{producto.descripcion}</p>
            <p className="price">${producto.precio}</p>
            <p className="category">Categoría: {producto.categoria}</p>
            
            {producto.tiempo_entrega && (
              <p className="delivery-time">
                <span className="icon">⏱️</span> Tiempo de entrega: {producto.tiempo_entrega}
              </p>
            )}
            
            {producto.materiales_disponibles && (
              <div className="materials">
                <p>Materiales disponibles:</p>
                <div className="material-tags">
                  {producto.materiales_disponibles.map((material, index) => (
                    <span key={index} className="material-tag">{material}</span>
                  ))}
                </div>
              </div>
            )}
            
            {producto.colores_disponibles && (
              <div className="colors">
                <p>Colores disponibles:</p>
                <div className="color-tags">
                  {producto.colores_disponibles.map((color, index) => (
                    <span key={index} className="color-tag">{color}</span>
                  ))}
                </div>
              </div>
            )}
            
            {producto.tamaño_maximo && (
              <p className="size">
                <span className="icon">📏</span> Tamaño máximo: {producto.tamaño_maximo}
              </p>
            )}
            
            {producto.incluye && (
              <div className="includes">
                <p>Incluye:</p>
                <ul>
                  {producto.incluye.map((item, index) => (
                    <li key={index}>{item}</li>
                  ))}
                </ul>
              </div>
            )}
            
            <button className="order-button">Solicitar</button>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ProductList; 