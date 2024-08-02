# services/IntegridadReferencialService.py

from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError
import logging
import io

class MemoryHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.log_stream = io.StringIO()

    def emit(self, record):
        msg = self.format(record)
        self.log_stream.write(msg + '\n')

    def get_logs(self):
        return self.log_stream.getvalue()

class IntegridadReferencialService:
    def __init__(self, engine):
        self.engine = engine
        self.inspector = inspect(engine)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.memory_handler = MemoryHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.memory_handler.setFormatter(formatter)
        self.logger.addHandler(self.memory_handler)

    def get_logs(self):
        return self.memory_handler.get_logs()

    def verificar_integridad_referencial(self):
        self.logger.info("Iniciando verificación de integridad referencial")
        try:
            anomalias = {
                "insercion": self.verificar_anomalias_insercion(),
                "eliminacion": self.verificar_anomalias_eliminacion(),
                "actualizacion": self.verificar_anomalias_actualizacion()
            }
            self.logger.info("Verificación de integridad referencial completada")
            return anomalias, None
        except SQLAlchemyError as e:
            self.logger.error(f"Error al verificar la integridad referencial: {str(e)}")
            return None, str(e)

    def verificar_anomalias_insercion(self):
        self.logger.info("Verificando anomalías de inserción")
        anomalias = []
        for table_name in self.inspector.get_table_names():
            fks = self.inspector.get_foreign_keys(table_name)
            for fk in fks:
                if 'options' not in fk or 'oninsert' not in fk['options']:
                    anomalia = {
                        "tabla": table_name,
                        "columna": fk['constrained_columns'][0],
                        "tipo": "Inserción",
                        "detalle": "No se ha definido acción para inserción en la clave foránea"
                    }
                    anomalias.append(anomalia)
                    self.logger.info(f"Anomalía de inserción detectada: {anomalia}")
        return anomalias

    def verificar_anomalias_eliminacion(self):
        self.logger.info("Verificando anomalías de eliminación")
        anomalias = []
        for table_name in self.inspector.get_table_names():
            fks = self.inspector.get_foreign_keys(table_name)
            for fk in fks:
                if 'options' not in fk or 'ondelete' not in fk['options']:
                    anomalia = {
                        "tabla": table_name,
                        "columna": fk['constrained_columns'][0],
                        "tipo": "Eliminación",
                        "detalle": "No se ha definido acción para eliminación en la clave foránea"
                    }
                    anomalias.append(anomalia)
                    self.logger.info(f"Anomalía de eliminación detectada: {anomalia}")
        return anomalias

    def verificar_anomalias_actualizacion(self):
        self.logger.info("Verificando anomalías de actualización")
        anomalias = []
        for table_name in self.inspector.get_table_names():
            fks = self.inspector.get_foreign_keys(table_name)
            for fk in fks:
                if 'options' not in fk or 'onupdate' not in fk['options']:
                    anomalia = {
                        "tabla": table_name,
                        "columna": fk['constrained_columns'][0],
                        "tipo": "Actualización",
                        "detalle": "No se ha definido acción para actualización en la clave foránea"
                    }
                    anomalias.append(anomalia)
                    self.logger.info(f"Anomalía de actualización detectada: {anomalia}")
        return anomalias

    def verificar_acciones_definidas(self):
        self.logger.info("Verificando acciones definidas en claves foráneas")
        acciones_definidas = {}
        for table_name in self.inspector.get_table_names():
            fks = self.inspector.get_foreign_keys(table_name)
            for fk in fks:
                acciones = {
                    "oninsert": fk.get('options', {}).get('oninsert', 'No definida'),
                    "ondelete": fk.get('options', {}).get('ondelete', 'No definida'),
                    "onupdate": fk.get('options', {}).get('onupdate', 'No definida')
                }
                acciones_definidas[f"{table_name}.{fk['constrained_columns'][0]}"] = acciones
                self.logger.info(f"Acciones definidas para {table_name}.{fk['constrained_columns'][0]}: {acciones}")
        return acciones_definidas

def check_integridad_referencial(engine):
    service = IntegridadReferencialService(engine)
    anomalias, error = service.verificar_integridad_referencial()
    acciones_definidas = service.verificar_acciones_definidas()
    logs = service.get_logs()
    return {
        "anomalias": anomalias,
        "acciones_definidas": acciones_definidas,
        "logs": logs
    }, error