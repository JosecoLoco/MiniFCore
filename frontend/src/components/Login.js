import React, { useState, useEffect } from 'react';
import './Login.css';

const Login = ({ onAuthSuccess }) => {
    const [isLogin, setIsLogin] = useState(true);
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        name: '',
        phoneExtension: '593',
        phoneNumber: '',
        city: ''
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [countryCode, setCountryCode] = useState('ec');

    useEffect(() => {
        // Actualizar el código del país cuando cambie la extensión
        if (formData.phoneExtension === '593') {
            setCountryCode('ec');
        }
    }, [formData.phoneExtension]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        
        // Validar que solo se ingresen números en los campos de teléfono
        if ((name === 'phoneExtension' || name === 'phoneNumber') && !/^\d*$/.test(value)) {
            return;
        }

        // Limitar la extensión a 3 dígitos
        if (name === 'phoneExtension' && value.length > 3) {
            return;
        }

        setFormData({
            ...formData,
            [name]: value
        });
        setError('');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const endpoint = isLogin ? '/api/auth/login' : '/api/auth/register';
            const url = `http://localhost:5000${endpoint}`;
            
            // Combinar la extensión y el número para el backend
            const submitData = isLogin ? {
                email: formData.email,
                password: formData.password
            } : {
                ...formData,
                phone: `+${formData.phoneExtension}${formData.phoneNumber}`
            };
            
            console.log('Intentando conectar a:', url);
            
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(submitData),
            });

            console.log('Respuesta recibida:', response.status);
            
            const data = await response.json();
            console.log('Datos recibidos:', data);

            if (!response.ok) {
                throw new Error(data.message || 'Error en la autenticación');
            }

            // Guardar el token en localStorage
            localStorage.setItem('token', data.token);
            localStorage.setItem('user', JSON.stringify(data.user));

            // Notificar al componente padre
            onAuthSuccess(data.user);

        } catch (err) {
            console.error('Error completo:', err);
            if (err.name === 'TypeError' && err.message === 'Failed to fetch') {
                setError('No se pudo conectar con el servidor. Por favor, verifica que el servidor esté corriendo.');
            } else {
                setError(err.message || 'Error al procesar la solicitud');
            }
        } finally {
            setLoading(false);
        }
    };

    const toggleMode = () => {
        setIsLogin(!isLogin);
        setError('');
        setFormData({
            email: '',
            password: '',
            name: '',
            phoneExtension: '593',
            phoneNumber: '',
            city: ''
        });
    };

    return (
        <div className="login-container">
            <div className="login-background"></div>
            <div className="login-content">
                <div className="login-box">
                    <div className="login-header">
                        <h1>3D Print Hub</h1>
                        <div className="printer-icon">
                            <span className="material-icons">3d_rotation</span>
                        </div>
                    </div>
                    {error && (
                        <div className="error-message">
                            <span className="material-icons">error</span>
                            {error}
                        </div>
                    )}
                    <form onSubmit={handleSubmit} className="login-form">
                        {!isLogin && (
                            <>
                                <div className="form-group">
                                    <div className="input-icon">
                                        <span className="material-icons">person</span>
                                        <input
                                            type="text"
                                            name="name"
                                            placeholder="Nombre completo"
                                            value={formData.name}
                                            onChange={handleChange}
                                            required={!isLogin}
                                        />
                                    </div>
                                </div>
                                <div className="form-group phone-group">
                                    <div className="phone-inputs">
                                        <div className="phone-extension">
                                            <span className="extension-prefix">+</span>
                                            <input
                                                type="text"
                                                name="phoneExtension"
                                                placeholder="593"
                                                value={formData.phoneExtension}
                                                onChange={handleChange}
                                                required={!isLogin}
                                                maxLength={3}
                                            />
                                        </div>
                                        <div className="phone-number">
                                            <input
                                                type="tel"
                                                name="phoneNumber"
                                                placeholder="Número de teléfono"
                                                value={formData.phoneNumber}
                                                onChange={handleChange}
                                                required={!isLogin}
                                            />
                                        </div>
                                        <div className="country-flag">
                                            <img 
                                                src={`https://flagcdn.com/w20/${countryCode}.png`}
                                                alt={`Bandera de ${countryCode.toUpperCase()}`}
                                                width="20"
                                                height="15"
                                            />
                                        </div>
                                    </div>
                                </div>
                                <div className="form-group">
                                    <div className="input-icon">
                                        <span className="material-icons">location_city</span>
                                        <input
                                            type="text"
                                            name="city"
                                            placeholder="Ciudad"
                                            value={formData.city}
                                            onChange={handleChange}
                                            required={!isLogin}
                                        />
                                    </div>
                                </div>
                            </>
                        )}
                        <div className="form-group">
                            <div className="input-icon">
                                <span className="material-icons">email</span>
                                <input
                                    type="email"
                                    name="email"
                                    placeholder="Correo electrónico"
                                    value={formData.email}
                                    onChange={handleChange}
                                    required
                                />
                            </div>
                        </div>
                        <div className="form-group">
                            <div className="input-icon">
                                <span className="material-icons">lock</span>
                                <input
                                    type="password"
                                    name="password"
                                    placeholder="Contraseña"
                                    value={formData.password}
                                    onChange={handleChange}
                                    required
                                />
                            </div>
                        </div>
                        <button type="submit" className="login-button" disabled={loading}>
                            {loading ? (
                                <span className="material-icons spinning">refresh</span>
                            ) : (
                                <>
                                    {isLogin ? 'Iniciar Sesión' : 'Registrarse'}
                                    <span className="button-icon material-icons">arrow_forward</span>
                                </>
                            )}
                        </button>
                    </form>
                    <div className="login-footer">
                        <p>{isLogin ? '¿No tienes una cuenta?' : '¿Ya tienes una cuenta?'}</p>
                        <button className="register-link" onClick={toggleMode}>
                            {isLogin ? 'Regístrate aquí' : 'Inicia sesión aquí'}
                        </button>
                    </div>
                </div>
                <div className="floating-shapes">
                    <div className="shape shape-1"></div>
                    <div className="shape shape-2"></div>
                    <div className="shape shape-3"></div>
                    <div className="shape shape-4"></div>
                </div>
            </div>
        </div>
    );
};

export default Login; 