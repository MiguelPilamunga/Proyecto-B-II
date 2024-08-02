from sqlalchemy import inspect, MetaData
from sqlalchemy.exc import SQLAlchemyError

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

    def get_all_columns(self):
        columns = []
        for table_name in self.inspector.get_table_names():
            for column in self.inspector.get_columns(table_name):
                columns.append((table_name, column['name']))
        return columns

    def get_all_pk_columns(self):
        pk_columns = []
        for table_name in self.inspector.get_table_names():
            pks = self.inspector.get_pk_constraint(table_name)
            if pks['constrained_columns']:
                for pk in pks['constrained_columns']:
                    pk_columns.append((table_name, pk))
        return pk_columns

    def get_all_fk_columns(self):
        fk_columns = []
        for table_name in self.inspector.get_table_names():
            for fk in self.inspector.get_foreign_keys(table_name):
                for fk_col in fk['constrained_columns']:
                    fk_columns.append((table_name, fk_col))
        return fk_columns

    def get_isolated_tables(self):
        all_columns = set(self.get_all_columns())
        fk_columns = set(self.get_all_fk_columns())

        referenced_tables = set()
        for table, _ in fk_columns:
            referenced_tables.add(table)

        isolated_tables = []
        for table, _ in all_columns:
            if table not in referenced_tables and table not in isolated_tables:
                isolated_tables.append(table)

        return [DataAnomaly("Tabla Aislada", table, details="Esta tabla no está referenciada por ninguna clave foránea") for table in isolated_tables]

    def get_false_fks(self):
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

        return false_fks

    def analyze_data_anomalies(self):
        try:
            isolated_tables = self.get_isolated_tables()
            false_fks = self.get_false_fks()

            return {
                "tablas_aisladas": isolated_tables,
                "claves_foraneas_falsas": false_fks
            }
        except SQLAlchemyError as e:
            return {"error": f"Ocurrió un error al analizar las anomalías de datos: {str(e)}"}

def check_data_anomalies(engine):
    service = DataAnomalyService(engine)
    anomalies = service.analyze_data_anomalies()
    return {
        "tablas_aisladas": [anomaly.to_dict() for anomaly in anomalies.get("tablas_aisladas", [])],
        "claves_foraneas_falsas": [anomaly.to_dict() for anomaly in anomalies.get("claves_foraneas_falsas", [])]
    }