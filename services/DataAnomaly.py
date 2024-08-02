import io
import logging
from sqlalchemy import inspect, MetaData
from sqlalchemy.exc import SQLAlchemyError


class MemoryHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.log_stream = io.StringIO()

    def emit(self, record):
        msg = self.format(record)
        self.log_stream.write(msg + '\n')

    def get_logs(self):
        return self.log_stream.getvalue()


class DataAnomaly:
    def __init__(self, anomaly_type, table_name, column_name=None, details=None):
        self.anomaly_type = anomaly_type
        self.table_name = table_name
        self.column_name = column_name
        self.details = details

    def to_dict(self):
        return {
            "tipo_anomalia": self.anomaly_type,
            "nombre_tabla": self.table_name,
            "nombre_columna": self.column_name,
            "detalles": self.details
        }


class DataAnomalyService:
    def __init__(self, engine):
        self.engine = engine
        self.inspector = inspect(engine)
        self.metadata = MetaData()
        self.metadata.reflect(bind=engine)

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.memory_handler = MemoryHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.memory_handler.setFormatter(formatter)
        self.logger.addHandler(self.memory_handler)

        self.logger.info("DataAnomalyService inicializado")

    def get_logs(self):
        return self.memory_handler.get_logs()

    def get_all_columns(self):
        self.logger.info("Obteniendo todas las columnas")
        columns = []
        for table_name in self.inspector.get_table_names():
            for column in self.inspector.get_columns(table_name):
                columns.append((table_name, column['name']))
        self.logger.info(f"Se obtuvieron {len(columns)} columnas")
        return columns

    def get_all_pk_columns(self):
        self.logger.info("Obteniendo todas las columnas de clave primaria")
        pk_columns = []
        for table_name in self.inspector.get_table_names():
            pks = self.inspector.get_pk_constraint(table_name)
            if pks['constrained_columns']:
                for pk in pks['constrained_columns']:
                    pk_columns.append((table_name, pk))
        self.logger.info(f"Se obtuvieron {len(pk_columns)} columnas de clave primaria")
        return pk_columns

    def get_all_fk_columns(self):
        self.logger.info("Obteniendo todas las columnas de clave foránea")
        fk_columns = []
        for table_name in self.inspector.get_table_names():
            for fk in self.inspector.get_foreign_keys(table_name):
                for fk_col in fk['constrained_columns']:
                    fk_columns.append((table_name, fk_col))
        self.logger.info(f"Se obtuvieron {len(fk_columns)} columnas de clave foránea")
        return fk_columns

    def get_isolated_tables(self):
        self.logger.info("Buscando tablas aisladas")
        all_columns = set(self.get_all_columns())
        fk_columns = set(self.get_all_fk_columns())

        referenced_tables = set()
        for table, _ in fk_columns:
            referenced_tables.add(table)

        isolated_tables = []
        for table, _ in all_columns:
            if table not in referenced_tables and table not in isolated_tables:
                isolated_tables.append(table)

        self.logger.info(f"Se encontraron {len(isolated_tables)} tablas aisladas")
        return [DataAnomaly("Tabla Aislada", table, details="Esta tabla no está referenciada por ninguna clave foránea")
                for table in isolated_tables]

    def get_false_fks(self):
        self.logger.info("Buscando claves foráneas falsas")
        all_columns = set(self.get_all_columns())
        pk_columns = set(self.get_all_pk_columns())
        fk_columns = set(self.get_all_fk_columns())

        non_fk_columns = all_columns - fk_columns
        false_fks = []

        for pk_table, pk_col in pk_columns:
            for table, col in non_fk_columns:
                if col == pk_col and table != pk_table:
                    false_fks.append(DataAnomaly("Clave Foránea Falsa", table, col,
                                                 f"Esta columna podría hacer referencia a {pk_table}.{pk_col} pero no es una clave foránea"))

        self.logger.info(f"Se encontraron {len(false_fks)} claves foráneas falsas")
        return false_fks

    def analyze_data_anomalies(self):
        self.logger.info("Iniciando análisis de anomalías de datos")
        try:
            isolated_tables = self.get_isolated_tables()
            false_fks = self.get_false_fks()

            self.logger.info("Análisis de anomalías completado")
            return {
                "tablas_aisladas": isolated_tables,
                "claves_foraneas_falsas": false_fks
            }
        except SQLAlchemyError as e:
            self.logger.error(f"Error durante el análisis de anomalías: {str(e)}")
            return {"error": f"Ocurrió un error al analizar las anomalías de datos: {str(e)}"}


def check_data_anomalies(engine):
    service = DataAnomalyService(engine)
    anomalies = service.analyze_data_anomalies()
    logs = service.get_logs()
    result = {
        "tablas_aisladas": [anomaly.to_dict() for anomaly in anomalies.get("tablas_aisladas", [])],
        "claves_foraneas_falsas": [anomaly.to_dict() for anomaly in anomalies.get("claves_foraneas_falsas", [])]
    }
    return result, logs