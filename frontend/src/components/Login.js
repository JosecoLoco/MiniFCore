import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Login.css';

function Login() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [nombre, setNombre] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (isLogin) {
        const response = await axios.post('http://localhost:5000/login', {
          email,
          password
        });
        
        if (response.data.token) {
          // Guardar el token y el rol en localStorage
          localStorage.setItem('token', response.data.token);
          localStorage.setItem('userRole', response.data.rol);
          
          // Redirigir según el rol
          if (response.data.rol === 'administrador') {
            navigate('/admin');
          } else {
            navigate('/user');
          }
        } else {
          setError('Error en la respuesta del servidor');
        }
      } else {
        // Registro de nuevo usuario
        const response = await axios.post('http://localhost:5000/register', {
          nombre,
          email,
          password,
          rol: 'usuario' // Por defecto, todos los registros son usuarios normales
        });

        if (response.data.mensaje) {
          setError('Registro exitoso. Por favor inicia sesión.');
          setIsLogin(true);
          setNombre('');
          setEmail('');
          setPassword('');
        }
      }
    } catch (err) {
      if (err.response && err.response.status === 401) {
        setError('Credenciales inválidas');
      } else if (err.response && err.response.status === 400) {
        setError(err.response.data.mensaje || 'Error en el registro');
      } else {
        setError('Error al conectar con el servidor');
      }
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h2>{isLogin ? 'Iniciar Sesión' : 'Registro de Usuario'}</h2>
        {error && <div className="error-message">{error}</div>}
        <form onSubmit={handleSubmit}>
          {!isLogin && (
            <div className="form-group">
              <label>Nombre:</label>
              <input
                type="text"
                value={nombre}
                onChange={(e) => setNombre(e.target.value)}
                required
              />
            </div>
          )}
          <div className="form-group">
            <label>Email:</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label>Contraseña:</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button type="submit" className="login-button">
            {isLogin ? 'Ingresar' : 'Registrarse'}
          </button>
        </form>
        <div className="switch-form">
          <button 
            className="switch-button"
            onClick={() => {
              setIsLogin(!isLogin);
              setError('');
            }}
          >
            {isLogin ? '¿No tienes cuenta? Regístrate' : '¿Ya tienes cuenta? Inicia sesión'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default Login; 