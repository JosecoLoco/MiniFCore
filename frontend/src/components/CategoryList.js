import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './CategoryList.css';

function CategoryList() {
  const [categorias, setCategorias] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCategorias = async () => {
      try {
        const response = await axios.get('http://localhost:5000/categorias');
        setCategorias(response.data);
        setLoading(false);
      } catch (err) {
        setError('Error al cargar las categorías');
        setLoading(false);
      }
    };

    fetchCategorias();
  }, []);

  if (loading) return <div className="loading">Cargando categorías...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="category-list">
      <h2>Categorías</h2>
      <div className="category-grid">
        {categorias.map((categoria) => (
          <div key={categoria._id} className="category-card">
            <h3>{categoria.nombre}</h3>
            <p>{categoria.descripcion}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default CategoryList; 