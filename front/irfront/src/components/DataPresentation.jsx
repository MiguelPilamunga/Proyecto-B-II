/* eslint-disable react/prop-types */
import { Box, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Typography, Button } from '@mui/material';

const DataPresentation = ({ data }) => {
    const anomalies = data[0]?.anomalies;
    const logs = data[1]?.logs;
    const resultado3 = data[2]?.resultado;
    const resultado4 = data[3]?.resultado;

    const downloadLogs = (logs) => {
        const blob = new Blob([logs], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'logs.txt';
        a.click();
        URL.revokeObjectURL(url);
    };

    const createDataRow = (anomaly) => (
        <TableRow key={`${anomaly.nombre_tabla}-${anomaly.nombre_columna}}`}>
            <TableCell>{anomaly.tipo_anomalia}</TableCell>
            <TableCell>{anomaly.nombre_tabla}</TableCell>
            <TableCell>{anomaly.nombre_columna}</TableCell>
            <TableCell>{anomaly.detalles}</TableCell>
        </TableRow>
    );

    // Create rows for anomaly table
    const createAnomalyRow = (anomaly) => (
        <TableRow key={`${anomaly.tabla}-${anomaly.columna}-${anomaly.tipo}`}>
            <TableCell>{anomaly.tipo}</TableCell>
            <TableCell>{anomaly.tabla}</TableCell>
            <TableCell>{anomaly.columna}</TableCell>
            <TableCell>{anomaly.detalle}</TableCell>
        </TableRow>
    );

    // Create rows for actions defined table
    const createActionRow = (key, action) => (
        <TableRow key={`${key}`}>
            <TableCell>{key.split('.')[0]}</TableCell>
            <TableCell>{key.split('.')[1]}</TableCell>
            <TableCell>{action.ondelete}</TableCell>
            <TableCell>{action.oninsert}</TableCell>
            <TableCell>{action.onupdate}</TableCell>
        </TableRow>
    );

    // Create rows for foreign keys table
    const createForeignKeyRow = (fk) => (
        <TableRow key={`${fk.tabla_hija}-${fk.columna_hija}-${fk.nombre_fk}`}>
            <TableCell>{fk.tabla_hija}</TableCell>
            <TableCell>{fk.columna_hija}</TableCell>
            <TableCell>{fk.tabla_padre}</TableCell>
            <TableCell>{fk.columna_padre}</TableCell>
            <TableCell>{fk.nombre_fk}</TableCell>
        </TableRow>
    );

    // Create rows for potential foreign keys table
    const createPotentialForeignKeyRow = (fk) => (
        <TableRow key={`${fk.tabla_hija}-${fk.columna_hija}-${fk.tabla_padre_potencial}`}>
            <TableCell>{fk.tabla_hija}</TableCell>
            <TableCell>{fk.columna_hija}</TableCell>
            <TableCell>{fk.tabla_padre_potencial}</TableCell>
            <TableCell>{fk.columna_padre_potencial}</TableCell>
        </TableRow>
    );

    // Compute counts
    const anomalyCount = (
        (anomalies?.claves_foraneas_falsas?.length || 0) +
        (anomalies?.tablas_aisladas?.length || 0) +
        (resultado3?.anomalias?.actualizacion?.length || 0) +
        (resultado3?.anomalias?.eliminacion?.length || 0) +
        (resultado3?.anomalias?.insercion?.length || 0)
    );
    const actionsCount = Object.keys(resultado3?.acciones_definidas || {}).length;
    const foreignKeyCount = resultado4?.existing_foreign_keys?.length || 0;
    const potentialForeignKeyCount = resultado4?.potential_foreign_keys?.length || 0;

    return (
        <Box display="flex" flexDirection="row">
            <Box flex={1} margin={2} display="flex" flexDirection="column">
                {/* Resultado 1: Anomalías Detectadas */}
                <Box marginBottom={2}>
                    <Typography variant="h6">Anomalías Detectadas ({anomalyCount})</Typography>
                    <TableContainer component={Paper}>
                        <Table>
                            <TableHead>
                                <TableRow>
                                    <TableCell>Tipo de Anomalía</TableCell>
                                    <TableCell>Tabla</TableCell>
                                    <TableCell>Columna</TableCell>
                                    <TableCell>Detalles</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {anomalies?.claves_foraneas_falsas?.map(createDataRow)}
                                {anomalies?.tablas_aisladas?.map(createDataRow)}
                                {resultado3?.anomalias?.actualizacion?.map(createAnomalyRow)}
                                {resultado3?.anomalias?.eliminacion?.map(createAnomalyRow)}
                                {resultado3?.anomalias?.insercion?.map(createAnomalyRow)}
                            </TableBody>
                        </Table>
                    </TableContainer>
                </Box>

                {/* Resultado 3: Acciones Definidas */}
                <Box marginBottom={2}>
                    <Typography variant="h6">Acciones Definidas ({actionsCount})</Typography>
                    <TableContainer component={Paper}>
                        <Table>
                            <TableHead>
                                <TableRow>
                                    <TableCell>Tabla</TableCell>
                                    <TableCell>Columna</TableCell>
                                    <TableCell>On Delete</TableCell>
                                    <TableCell>On Insert</TableCell>
                                    <TableCell>On Update</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {Object.entries(resultado3?.acciones_definidas || {}).map(([key, action]) =>
                                    createActionRow(key, action)
                                )}
                            </TableBody>
                        </Table>
                    </TableContainer>
                </Box>

                {/* Resultado 4: Claves Foráneas Existentes */}
                <Box marginBottom={2}>
                    <Typography variant="h6">Claves Foráneas Existentes ({foreignKeyCount})</Typography>
                    <TableContainer component={Paper}>
                        <Table>
                            <TableHead>
                                <TableRow>
                                    <TableCell>Tabla Hija</TableCell>
                                    <TableCell>Columna Hija</TableCell>
                                    <TableCell>Tabla Padre</TableCell>
                                    <TableCell>Columna Padre</TableCell>
                                    <TableCell>Nombre FK</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {resultado4?.existing_foreign_keys?.map(createForeignKeyRow)}
                            </TableBody>
                        </Table>
                    </TableContainer>
                </Box>

                {/* Resultado 4: Claves Foráneas Potenciales */}
                <Box marginBottom={2}>
                    <Typography variant="h6">Claves Foráneas Potenciales ({potentialForeignKeyCount})</Typography>
                    <TableContainer component={Paper}>
                        <Table>
                            <TableHead>
                                <TableRow>
                                    <TableCell>Tabla Hija</TableCell>
                                    <TableCell>Columna Hija</TableCell>
                                    <TableCell>Tabla Padre Potencial</TableCell>
                                    <TableCell>Columna Padre Potencial</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {resultado4?.potential_foreign_keys?.map(createPotentialForeignKeyRow)}
                            </TableBody>
                        </Table>
                    </TableContainer>
                </Box>
            {/* Descargar Logs */}
            {logs && (
                <Box flex={1} margin={2}>
                    <Button onClick={() => downloadLogs(logs)}>Descargar Logs</Button>
                </Box>
            )}
            </Box>

            {/* JSON Original */}
            <Box flex={1} margin={2}>
                <Typography variant="h6">JSON Original</Typography>
                <Paper style={{ maxHeight: '80vh', overflow: 'auto' }}>
                    <pre>{JSON.stringify(data, null, 2)}</pre>
                </Paper>
            </Box>


        </Box>
    );
};

export default DataPresentation;
