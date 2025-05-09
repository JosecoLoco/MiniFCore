import React, { useState, useEffect } from 'react';
import './PrintJobsList.css';

const PrintJobsList = () => {
    const [jobs, setJobs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchJobs();
    }, []);

    const fetchJobs = async () => {
        try {
            const response = await fetch('http://localhost:5000/api/print-jobs');
            if (!response.ok) {
                throw new Error('Error al cargar los trabajos');
            }
            const data = await response.json();
            setJobs(data);
            setLoading(false);
        } catch (err) {
            setError(err.message);
            setLoading(false);
        }
    };

    if (loading) return <div className="loading">Cargando trabajos...</div>;
    if (error) return <div className="error">{error}</div>;

    return (
        <div className="print-jobs-container">
            <h2>Trabajos de Impresión</h2>
            <div className="jobs-grid">
                {jobs.map((job) => (
                    <div key={job._id} className="job-card">
                        <h3>{job.name}</h3>
                        <p>{job.description}</p>
                        <div className="job-status">
                            <span className={`status-badge ${job.status}`}>
                                {job.status}
                            </span>
                        </div>
                        <div className="job-dates">
                            <p>Creado: {new Date(job.created_at).toLocaleDateString()}</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default PrintJobsList; 