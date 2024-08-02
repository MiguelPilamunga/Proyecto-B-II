import { useState } from 'react';

const AuditForm = () => {
  const [formData, setFormData] = useState({
    server: '',
    database: '',
    username: '',
    password: '',
  });
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:5000/integridad/check', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams(formData),
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      if (data.status === 'error') {
        throw new Error(data.message);
      }
      
      setResults(data);
      setError(null);
    } catch (err) {
      setError("Error en comunicación con DB");
      setResults(null);
    }
  };

  const renderResults = () => {
    if (!results) return null;

    const {
      status = '',
      message = '',
      total_violations = 0,
      violation_summary = [],
      detailed_results = {}
    } = results;

    return (
      <div>
        <h2>Resultado de la Auditoría</h2>
        <p>Status: {status}</p>
        <p>Mensaje: {message}</p>
        <p>Total de Errores: {total_violations}</p>
        {violation_summary.length > 0 && (
          <ul>
            {violation_summary.map((explanation, index) => (
              <li key={index}>{explanation}</li>
            ))}
          </ul>
        )}
        <h3>Detalles:</h3>
        <div>
          <h4>Violaciones de tipo de datos:</h4>
          {Array.isArray(detailed_results.data_type_mismatch) && detailed_results.data_type_mismatch.length > 0 ? (
            <ul>
              {detailed_results.data_type_mismatch.map((item, index) => (
                <li key={index}>
                  {item.ForeignKeyName} en la tabla {item.TableName} ({item.ColumnName})
                  - Tipo de dato: {item.ColumnDataType} no coincide con {item.ReferencedColumnDataType} en la tabla {item.ReferencedTableName} ({item.ReferencedColumnName})
                </li>
              ))}
            </ul>
          ) : <p>No hay violaciones de tipo de datos.</p>}
        </div>
        <div>
          <h4>Claves primarias duplicadas:</h4>
          {Array.isArray(detailed_results.duplicate_primary_keys) && detailed_results.duplicate_primary_keys.length > 0 ? (
            <ul>
              {detailed_results.duplicate_primary_keys.map((item, index) => (
                <li key={index}>{item.Issue}: {item.DuplicateCount} duplicados</li>
              ))}
            </ul>
          ) : <p>No hay claves primarias duplicadas.</p>}
        </div>
        <div>
          <h4>Claves foráneas sin índice:</h4>
          {Array.isArray(detailed_results.foreign_keys_without_index) && detailed_results.foreign_keys_without_index.length > 0 ? (
            <ul>
              {detailed_results.foreign_keys_without_index.map((item, index) => (
                <li key={index}>{item.TableName} ({item.ColumnName})</li>
              ))}
            </ul>
          ) : <p>No hay claves foráneas sin índice.</p>}
        </div>
        <div>
          <h4>Registros huérfanos:</h4>
          {Array.isArray(detailed_results.orphaned_records) && detailed_results.orphaned_records.length > 0 ? (
            <ul>
              {detailed_results.orphaned_records.map((item, index) => (
                <li key={index}>
                  Tabla Hija: {item.ChildTable} ({item.ChildColumn}) tiene {item.OrphanCount} registros huérfanos sin correspondencia en la Tabla Padre: {item.ParentTable} ({item.ParentColumn})
                </li>
              ))}
            </ul>
          ) : <p>No hay registros huérfanos.</p>}
        </div>
        <div>
          <h4>Incompatibilidad en nulabilidad:</h4>
          {Array.isArray(detailed_results.nullability_mismatch) && detailed_results.nullability_mismatch.length > 0 ? (
            <ul>
              {detailed_results.nullability_mismatch.map((item, index) => (
                <li key={index}>
                  Clave Foránea: {item.ForeignKeyName} en la tabla {item.TableName} ({item.ColumnName}) tiene una nulabilidad que no coincide con la columna referenciada {item.ReferencedColumnName} en la tabla {item.ReferencedTableName}
                </li>
              ))}
            </ul>
          ) : <p>No hay incompatibilidad en nulabilidad.</p>}
        </div>
      </div>
    );
  };

  return (
    <div>
      <h1>Trabajo 3 - Auditoria de Integridad Referencial</h1>
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
      {error && <p className="error">{error}</p>}
      {renderResults()}
    </div>
  );
};

export default AuditForm;
