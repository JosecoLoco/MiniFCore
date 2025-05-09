import React, { useState, useEffect } from 'react';
import './Home.css';

const Home = () => {
    const [categories, setCategories] = useState([]);
    const [products, setProducts] = useState([]);
    const [selectedCategory, setSelectedCategory] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchCategories();
    }, []);

    useEffect(() => {
        if (selectedCategory) {
            fetchProducts(selectedCategory);
        } else {
            fetchProducts();
        }
    }, [selectedCategory]);

    const fetchCategories = async () => {
        try {
            const response = await fetch('http://localhost:5000/api/categories');
            if (!response.ok) throw new Error('Error al cargar categorías');
            const data = await response.json();
            setCategories(data);
        } catch (err) {
            setError('Error al cargar las categorías');
            console.error('Error:', err);
        }
    };

    const fetchProducts = async (categoryId = null) => {
        setLoading(true);
        try {
            const url = categoryId 
                ? `http://localhost:5000/api/products?category_id=${categoryId}`
                : 'http://localhost:5000/api/products';
            const response = await fetch(url);
            if (!response.ok) throw new Error('Error al cargar productos');
            const data = await response.json();
            setProducts(data);
        } catch (err) {
            setError('Error al cargar los productos');
            console.error('Error:', err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="home-container">
            <div className="categories-section">
                <h2>Categorías</h2>
                <div className="categories-grid">
                    {categories.map(category => (
                        <div 
                            key={category._id}
                            className={`category-card ${selectedCategory === category._id ? 'selected' : ''}`}
                            onClick={() => setSelectedCategory(category._id)}
                        >
                            <span className="material-icons category-icon">{category.icon}</span>
                            <h3>{category.name}</h3>
                            <p>{category.description}</p>
                        </div>
                    ))}
                </div>
            </div>

            <div className="products-section">
                <h2>Productos {selectedCategory ? 'de ' + categories.find(c => c._id === selectedCategory)?.name : ''}</h2>
                {error && <div className="error-message">{error}</div>}
                {loading ? (
                    <div className="loading">
                        <span className="material-icons spinning">refresh</span>
                        Cargando productos...
                    </div>
                ) : (
                    <div className="products-grid">
                        {products.map(product => (
                            <div key={product._id} className="product-card">
                                {product.images && product.images[0] && (
                                    <img 
                                        src={product.images[0]} 
                                        alt={product.name}
                                        className="product-image"
                                    />
                                )}
                                <div className="product-info">
                                    <h3>{product.name}</h3>
                                    <p>{product.description}</p>
                                    <div className="product-details">
                                        <span className="price">${product.price}</span>
                                        <span className="material">Material: {product.material}</span>
                                        <span className="print-time">Tiempo: {product.print_time}</span>
                                    </div>
                                    <button className="order-button">
                                        <span className="material-icons">shopping_cart</span>
                                        Ordenar
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default Home; 