import React, { useState } from 'react';
import axios from 'axios';

const AuditForm = () => {
  const [server, setServer] = useState('');
  const [database, setDatabase] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await axios.post('http://localhost:5000/integridad/check', new URLSearchParams({
        server,
        database,
        username,
        password
      }).toString(), {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });

      setResult(response.data);
    } catch (err) {
      setError('Error al consultar la integridad de la base de datos.');
    } finally {
      setLoading(false);
    }
  };

  const renderResults = () => {
    if (!result) return null;

    const { status, message, total_violations, violation_summary, detailed_results } = result;

    return (
      <div>
        <h2>Resultado de la Auditoría</h2>
        <p>Status: {status}</p>
        <p>Message: {message}</p>
        <p>Total Violations: {total_violations}</p>
        {violation_summary && violation_summary.length > 0 && (
          <ul>
            {violation_summary.map((explanation, index) => (
              <li key={index}>{explanation}</li>
            ))}
          </ul>
        )}
        <h3>Detalles:</h3>
        <div>
          <h4>Violaciones de tipo de datos:</h4>
          {detailed_results.data_type_mismatch && detailed_results.data_type_mismatch.length > 0 ? (
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
          {detailed_results.duplicate_primary_keys && detailed_results.duplicate_primary_keys.length > 0 ? (
            <ul>
              {detailed_results.duplicate_primary_keys.map((item, index) => (
                <li key={index}>{item.Issue}: {item.DuplicateCount} duplicados</li>
              ))}
            </ul>
          ) : <p>No hay claves primarias duplicadas.</p>}
        </div>
        <div>
          <h4>Claves foráneas sin índice:</h4>
          {detailed_results.foreign_keys_without_index && detailed_results.foreign_keys_without_index.length > 0 ? (
            <ul>
              {detailed_results.foreign_keys_without_index.map((item, index) => (
                <li key={index}>{item.TableName} ({item.ColumnName})</li>
              ))}
            </ul>
          ) : <p>No hay claves foráneas sin índice.</p>}
        </div>
        <div>
          <h4>Registros huérfanos:</h4>
          {detailed_results.orphaned_records && detailed_results.orphaned_records.length > 0 ? (
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
          {detailed_results.nullability_mismatch && detailed_results.nullability_mismatch.length > 0 ? (
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
    <form onSubmit={handleSubmit}>
      <h2>Formulario de Auditoría de Integridad</h2>
      <div>
        <label>Servidor:</label>
        <input type="text" value={server} onChange={(e) => setServer(e.target.value)} />
      </div>
      <div>
        <label>Base de Datos:</label>
        <input type="text" value={database} onChange={(e) => setDatabase(e.target.value)} />
      </div>
      <div>
        <label>Usuario:</label>
        <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} />
      </div>
      <div>
        <label>Contraseña:</label>
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
      </div>
      <button type="submit" disabled={loading}>Enviar</button>
      {loading && <p>Cargando...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {renderResults()}
    </form>
  );
};

export default AuditForm;
