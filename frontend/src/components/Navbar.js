import React from 'react';
import { Link } from 'react-router-dom';
import './Navbar.css';

function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <h1>3D Store</h1>
      </div>
      <ul className="navbar-nav">
        <li className="nav-item">
          <Link to="/" className="nav-link">Inicio</Link>
        </li>
        <li className="nav-item">
          <Link to="/productos" className="nav-link">Productos</Link>
        </li>
        <li className="nav-item">
          <Link to="/categorias" className="nav-link">Categorías</Link>
        </li>
        <li className="nav-item">
          <Link to="/usuarios" className="nav-link">Usuarios</Link>
        </li>
      </ul>
    </nav>
  );
}

export default Navbar; 