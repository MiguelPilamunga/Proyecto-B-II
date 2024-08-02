import pandas as pd
from sqlalchemy import inspect, text
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


class IntegridadReferencialRelacionalService:
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

    def get_existing_foreign_keys(self):
        self.logger.info("Obteniendo claves foráneas existentes")
        existing_fks = []
        for table_name in self.inspector.get_table_names():
            fks = self.inspector.get_foreign_keys(table_name)
            for fk in fks:
                existing_fks.append({
                    'tabla_hija': table_name,
                    'columna_hija': fk['constrained_columns'][0],
                    'tabla_padre': fk['referred_table'],
                    'columna_padre': fk['referred_columns'][0],
                    'nombre_fk': fk['name']
                })
        return pd.DataFrame(existing_fks)

    def get_potential_foreign_keys(self):
        self.logger.info("Identificando potenciales claves foráneas")
        potential_fks = []
        tables = self.inspector.get_table_names()
        for table in tables:
            columns = self.inspector.get_columns(table)
            for column in columns:
                if column['name'].endswith('_id') or column['name'].startswith('id_'):
                    potential_parent = column['name'].replace('_id', '').replace('id_', '')
                    if potential_parent in tables:
                        potential_fks.append({
                            'tabla_hija': table,
                            'columna_hija': column['name'],
                            'tabla_padre_potencial': potential_parent,
                            'columna_padre_potencial': 'id'  # Asumimos que la columna padre es 'id'
                        })
        return pd.DataFrame(potential_fks)

    def get_missing_foreign_keys(self):
        self.logger.info("Identificando claves foráneas faltantes")
        existing_fks = self.get_existing_foreign_keys()
        potential_fks = self.get_potential_foreign_keys()

        # Convertimos existing_fks a un conjunto de tuplas para facilitar la comparación
        existing_fk_set = set(
            (row['tabla_hija'], row['columna_hija'], row['tabla_padre'], row['columna_padre'])
            for _, row in existing_fks.iterrows()
        )

        missing_fks = []
        for _, row in potential_fks.iterrows():
            potential_fk = (
            row['tabla_hija'], row['columna_hija'], row['tabla_padre_potencial'], row['columna_padre_potencial'])
            if potential_fk not in existing_fk_set:
                missing_fks.append({
                    'tabla_hija': row['tabla_hija'],
                    'columna_hija': row['columna_hija'],
                    'tabla_padre_potencial': row['tabla_padre_potencial'],
                    'columna_padre_potencial': row['columna_padre_potencial']
                })

        return pd.DataFrame(missing_fks)

    def analyze_referential_relationships(self):
        self.logger.info("Iniciando análisis de relaciones referenciales")
        existing_fks = self.get_existing_foreign_keys()
        potential_fks = self.get_potential_foreign_keys()
        missing_fks = self.get_missing_foreign_keys()

        num_existing_fks = len(existing_fks)
        num_potential_fks = len(potential_fks)
        num_missing_fks = len(missing_fks)
        num_anomalies = num_potential_fks - num_existing_fks

        results = {
            "existing_foreign_keys": existing_fks.to_dict(orient='records'),
            "potential_foreign_keys": potential_fks.to_dict(orient='records'),
            "missing_foreign_keys": missing_fks.to_dict(orient='records'),
            "num_existing_fks": num_existing_fks,
            "num_potential_fks": num_potential_fks,
            "num_missing_fks": num_missing_fks,
            "num_anomalies": num_anomalies
        }

        self.logger.info(f"Se encontraron {num_existing_fks} claves foráneas existentes")
        self.logger.info(f"Se identificaron {num_potential_fks} potenciales claves foráneas")
        self.logger.info(f"Se detectaron {num_missing_fks} claves foráneas faltantes")
        self.logger.info(f"Se detectaron {num_anomalies} anomalías en las relaciones referenciales")
        self.logger.info("Análisis de relaciones referenciales completado")

        return results


def check_relations(engine):
    service = IntegridadReferencialRelacionalService(engine)
    results = service.analyze_referential_relationships()
    logs = service.get_logs()
    return results, logs

