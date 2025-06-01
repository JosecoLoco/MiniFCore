import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './UserList.css';

function UserList() {
  const [usuarios, setUsuarios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchUsuarios = async () => {
      try {
        const response = await axios.get('http://localhost:5000/usuarios');
        setUsuarios(response.data);
        setLoading(false);
      } catch (err) {
        setError('Error al cargar los usuarios');
        setLoading(false);
      }
    };

    fetchUsuarios();
  }, []);

  if (loading) return <div className="loading">Cargando usuarios...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="user-list">
      <h2>Usuarios</h2>
      <div className="user-grid">
        {usuarios.map((usuario) => (
          <div key={usuario._id} className="user-card">
            <div className="user-avatar">
              {usuario.nombre.charAt(0).toUpperCase()}
            </div>
            <div className="user-info">
              <h3>{usuario.nombre}</h3>
              <p className="user-email">{usuario.email}</p>
              <span className={`user-role ${usuario.rol}`}>
                {usuario.rol}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default UserList; 