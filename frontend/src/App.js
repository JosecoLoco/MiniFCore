import React, { useState, useEffect } from 'react';
import './App.css';
import Login from './components/Login';
import PrintJobsList from './components/PrintJobsList';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Verificar si hay un token guardado
    const token = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');
    if (token && savedUser) {
      setIsAuthenticated(true);
      setUser(JSON.parse(savedUser));
    }
  }, []);

  const handleAuthSuccess = (userData) => {
    setIsAuthenticated(true);
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setIsAuthenticated(false);
    setUser(null);
  };

  return (
    <div className="App">
      {!isAuthenticated ? (
        <Login onAuthSuccess={handleAuthSuccess} />
      ) : (
        <>
          <header className="App-header">
            <div className="header-content">
              <h1>Sistema de Impresiones 3D</h1>
              <div className="user-info">
                <span>Bienvenido, {user?.name}</span>
                <button onClick={handleLogout} className="logout-button">
                  <span className="material-icons">logout</span>
                  Cerrar sesión
                </button>
              </div>
            </div>
          </header>
          <main>
            <PrintJobsList />
          </main>
        </>
      )}
    </div>
  );
}

export default App;
