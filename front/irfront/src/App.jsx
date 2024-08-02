import { useState } from 'react';
import axios from 'axios';
import DataPresentation from './components/DataPresentation';

const AuditForm = () => {
  const [formData, setFormData] = useState({
      server: '',
      database: '',
      username: '',
      password: '',
  });
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
      const { name, value } = e.target;
      setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
      e.preventDefault();
      setLoading(true);
      setError(null);
      setResults([]);

      const endpoints = [
          'http://localhost:5000/auditoria/check_anomalies',
          'http://localhost:5000/auditoria/get_anomaly_logs',
          'http://localhost:5000/integridad_referencial/check',
          'http://localhost:5000/integridad_relacional/check'
      ];

      try {
          const responses = await Promise.all(endpoints.map(endpoint =>
              axios.post(endpoint, new URLSearchParams(formData), {
                  headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
              })
          ));
          setResults(responses.map(response => response.data));
      } catch (err) {
          setError("Error en comunicación con DB");
      } finally {
          setLoading(false);
      }
  };

  return (
      <div>
          <h1>Trabajo 3 - Auditoria Informática - EPN</h1>
          <form onSubmit={handleSubmit}>
              <div className="form-grid">
                  <div>
                      <label htmlFor="server">Servidor:</label>
                      <input
                          type="text"
                          id="server"
                          name="server"
                          value={formData.server}
                          onChange={handleChange}
                      />
                  </div>
                  <div>
                      <label htmlFor="database">Base de datos:</label>
                      <input
                          type="text"
                          id="database"
                          name="database"
                          value={formData.database}
                          onChange={handleChange}
                      />
                  </div>
                  <div>
                      <label htmlFor="username">Usuario:</label>
                      <input
                          type="text"
                          id="username"
                          name="username"
                          value={formData.username}
                          onChange={handleChange}
                      />
                  </div>
                  <div>
                      <label htmlFor="password">Contraseña:</label>
                      <input
                          type="password"
                          id="password"
                          name="password"
                          value={formData.password}
                          onChange={handleChange}
                      />
                  </div>
              </div>
              <button type="submit">Enviar</button>
          </form>
          {loading && <p>Cargando...</p>}
          {error && <p className="error">{error}</p>}
          {results.length > 0 && <DataPresentation data={results} />}
      </div>
  );
};

export default AuditForm;