import React, { useState } from 'react';
import axios from 'axios';

const App = () => {
  const [formData, setFormData] = useState({
    server: '',
    database: '',
    username: '',
    password: '',
    port: ''
  });
  const [tableData, setTableData] = useState({});
  const [integrityResults, setIntegrityResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [noData, setNoData] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setNoData(false);

    // Limpiar los resultados anteriores
    setTableData({});
    setIntegrityResults([]);

    try {
      const response = await axios.post('http://localhost:5000/test-db', formData);
      if (response.data.error) {
        setNoData(true);
      } else {
        setTableData(response.data.table_data);
        setIntegrityResults(response.data.integrity_results);
      }
    } catch (error) {
      setError('Error al conectar con la base de datos.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Auditoría de Base de Datos</h1>

      <form onSubmit={handleSubmit}>
        <div>
          <label>Server:</label>
          <input
            type="text"
            name="server"
            value={formData.server}
            onChange={handleChange}
            required
          />
        </div>
        <div>
          <label>Database:</label>
          <input
            type="text"
            name="database"
            value={formData.database}
            onChange={handleChange}
            required
          />
        </div>
        <div>
          <label>Username:</label>
          <input
            type="text"
            name="username"
            value={formData.username}
            onChange={handleChange}
            required
          />
        </div>
        <div>
          <label>Password:</label>
          <input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            required
          />
        </div>
        <div>
          <label>Port:</label>
          <input
            type="text"
            name="port"
            value={formData.port}
            onChange={handleChange}
            required
          />
        </div>
        <button type="submit">Auditar</button>
      </form>

      {loading && <p>Cargando...</p>}
      {error && <p>{error}</p>}
      {noData && <p>Base de datos no encontrada o datos incorrectos.</p>}

      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '20px' }}>
        <div style={{ flex: 1, marginRight: '10px', overflow: 'auto' }}>
          <h2>Datos de Tablas</h2>
          {Object.keys(tableData).length > 0 ? (
            Object.keys(tableData).map((table) => (
              <div key={table}>
                <h3>{table}</h3>
                <table border="1" style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr>
                      {tableData[table].length > 0 &&
                        Object.keys(tableData[table][0]).map((key) => (
                          <th key={key} style={{ padding: '8px', border: '1px solid black' }}>{key}</th>
                        ))}
                    </tr>
                  </thead>
                  <tbody>
                    {tableData[table].map((row, index) => (
                      <tr key={index}>
                        {Object.values(row).map((value, idx) => (
                          <td key={idx} style={{ padding: '8px', border: '1px solid black' }}>{value}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ))
          ) : (
            <p>No se encontraron datos para mostrar.</p>
          )}
        </div>

        <div style={{ flex: 1, marginLeft: '10px', overflow: 'auto' }}>
          <h2>Resultados de Integridad Referencial</h2>
          {integrityResults.length > 0 ? (
            <ul>
              {integrityResults.map((result, index) => (
                <li key={index}>
                  <strong>Tabla:</strong> {result.table}, <strong>Clave Foránea:</strong> {result.foreign_key}, 
                  <strong>Registros Huérfanos:</strong> {result.result.length}
                </li>
              ))}
            </ul>
          ) : (
            <p>No se encontraron anomalías.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default App;
