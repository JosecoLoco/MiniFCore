import React, { useState, useEffect } from 'react';
import Login from './components/Login';
import Home from './components/Home';
import './App.css';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [lastActivity, setLastActivity] = useState(Date.now());

  useEffect(() => {
    // Verificar si hay un usuario guardado en localStorage
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
    setLoading(false);

    // Configurar eventos para detectar actividad
    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];
    const updateActivity = () => setLastActivity(Date.now());

    events.forEach(event => {
      document.addEventListener(event, updateActivity);
    });

    return () => {
      events.forEach(event => {
        document.removeEventListener(event, updateActivity);
      });
    };
  }, []);

  useEffect(() => {
    if (!user) return;

    const checkSession = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          handleLogout();
          return;
        }

        const response = await fetch('http://localhost:5000/api/auth/check-session', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) {
          handleLogout();
        }
      } catch (error) {
        console.error('Error checking session:', error);
        handleLogout();
      }
    };

    const inactivityCheck = setInterval(() => {
      const now = Date.now();
      const inactiveTime = now - lastActivity;
      
      if (inactiveTime > 15000) { // 15 segundos
        handleLogout();
      } else {
        checkSession();
      }
    }, 5000); // Verificar cada 5 segundos

    return () => clearInterval(inactivityCheck);
  }, [user, lastActivity]);

  const handleAuthSuccess = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  if (loading) {
    return (
      <div className="loading-screen">
        <span className="material-icons spinning">refresh</span>
        Cargando...
      </div>
    );
  }

  return (
    <div className="app">
      {!user ? (
        <Login onAuthSuccess={handleAuthSuccess} />
      ) : (
        <div className="app-container">
          <header className="app-header">
            <div className="header-content">
              <h1>3D Print Hub</h1>
              <div className="user-info">
                <span className="user-name">{user.name}</span>
                <button className="logout-button" onClick={handleLogout}>
                  <span className="material-icons">logout</span>
                  Cerrar Sesión
                </button>
              </div>
            </div>
          </header>
          <main>
            <Home />
          </main>
        </div>
      )}
    </div>
  );
}

export default App;
