from sqlalchemy import create_engine, Column, Integer, String, DateTime, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import re
import pymssql

Base = declarative_base()

class AuditoriaLog(Base):
    __tablename__ = 'auditoria_log'
    id = Column(Integer, primary_key=True)
    tabla = Column(String)
    operacion = Column(String)
    usuario = Column(String)
    fecha_hora = Column(DateTime)
    datos = Column(String)

class AuditModel:
    def __init__(self, server, database, username, password):
        self.engine = create_engine(f'mssql+pymssql://{username}:{password}@{server}/{database}')
        self.Session = sessionmaker(bind=self.engine)
        self.crear_tabla_auditoria()

    def crear_tabla_auditoria(self):
        inspector = inspect(self.engine)
        if 'auditoria_log' not in inspector.get_table_names():
            Base.metadata.create_all(self.engine)
            with self.engine.connect() as conn:
                conn.execute(text("ALTER TABLE auditoria_log ADD datos NVARCHAR(MAX)"))
            print("Tabla auditoria_log creada")
        else:
            print("La tabla auditoria_log ya existe")

    def recrear_tabla_auditoria(self):
        with self.engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS auditoria_log"))
        Base.metadata.create_all(self.engine)
        with self.engine.connect() as conn:
            conn.execute(text("ALTER TABLE auditoria_log ADD datos NVARCHAR(MAX)"))
        print("Tabla auditoria_log recreada")

    def analizar_consulta(self, query):
        insert_pattern = r"INSERT\s+INTO\s+(\w+)\s*\((.*?)\)\s*VALUES\s*\((.*?)\)"
        update_pattern = r"UPDATE\s+(\w+)\s+SET\s+(.*?)\s*WHERE\s+(.*)"
        delete_pattern = r"DELETE\s+FROM\s+(\w+)\s*WHERE\s+(.*)"

        if re.match(insert_pattern, query, re.IGNORECASE):
            match = re.match(insert_pattern, query, re.IGNORECASE)
            return 'INSERT', match.group(1), dict(
                zip(map(str.strip, match.group(2).split(',')), map(str.strip, match.group(3).split(','))))
        elif re.match(update_pattern, query, re.IGNORECASE):
            match = re.match(update_pattern, query, re.IGNORECASE)
            return 'UPDATE', match.group(1), {item.split('=')[0].strip(): item.split('=')[1].strip() for item in
                                              match.group(2).split(',')}
        elif re.match(delete_pattern, query, re.IGNORECASE):
            match = re.match(delete_pattern, query, re.IGNORECASE)
            return 'DELETE', match.group(1), match.group(2)
        else:
            return None, None, None

    def auditar_operacion(self, query):
        operacion, tabla, valores = self.analizar_consulta(query)
        if not operacion:
            return {"status": "error", "message": "Consulta no reconocida o no compatible con la auditoría"}

        columnas_info = self.verificar_estructura_tabla(tabla)
        if not columnas_info:
            return {"status": "error", "message": f"La tabla {tabla} no existe o no tiene columnas"}

        if operacion == 'INSERT':
            columnas_query = set(valores.keys())
            columnas_tabla = set(columnas_info.keys())
            columnas_faltantes = columnas_query - columnas_tabla
            if columnas_faltantes:
                return {"status": "error",
                        "message": f"Las siguientes columnas no existen en la tabla: {', '.join(columnas_faltantes)}"}

            if 'id' in columnas_tabla and 'id' not in valores:
                siguiente_id = self.obtener_siguiente_id(tabla)
                valores['id'] = str(siguiente_id)

            # Reconstruir la consulta con el nuevo ID
            columnas = ', '.join(valores.keys())
            valores_str = ', '.join(f"'{v}'" if not v.isnumeric() else v for v in valores.values())
            query = f"INSERT INTO {tabla} ({columnas}) VALUES ({valores_str})"

        self.crear_trigger_auditoria(tabla)

        try:
            with self.engine.connect() as conn:
                conn.execute(text(query))

            log_query = text(f"""
            SELECT TOP 1 * FROM auditoria_log
            WHERE tabla = :tabla AND operacion = :operacion
            ORDER BY fecha_hora DESC
            """)
            with self.engine.connect() as conn:
                result = conn.execute(log_query, {"tabla": tabla, "operacion": operacion})
                log = result.fetchone()

            return {
                "status": "success",
                "message": f"Operación {operacion} ejecutada con éxito en la tabla {tabla}",
                "operacion": operacion,
                "tabla": tabla,
                "valores": valores,
                "query_ejecutada": query,
                "log_auditoria": dict(log) if log else None
            }
        except Exception as e:
            return {"status": "error", "message": f"Error al ejecutar la consulta: {str(e)}", "query_intentada": query}

    def verificar_estructura_tabla(self, tabla):
        inspector = inspect(self.engine)
        columns = inspector.get_columns(tabla)
        if not columns:
            return None
        return {col['name']: col['type'] for col in columns}

    def obtener_siguiente_id(self, tabla):
        query = text(f"SELECT ISNULL(MAX(id), 0) + 1 as next_id FROM {tabla}")
        with self.engine.connect() as conn:
            result = conn.execute(query)
            next_id = result.fetchone()
        return next_id[0] if next_id else 1

    def crear_trigger_auditoria(self, tabla):
        triggers = {
            'insert': f"""
            CREATE TRIGGER tr_{tabla}_insert ON {tabla}
            AFTER INSERT
            AS
            BEGIN
                INSERT INTO auditoria_log (tabla, operacion, usuario, fecha_hora, datos)
                SELECT '{tabla}', 'INSERT', SYSTEM_USER, GETDATE(), (SELECT * FROM inserted FOR JSON PATH)
            END
            """,
            'update': f"""
            CREATE TRIGGER tr_{tabla}_update ON {tabla}
            AFTER UPDATE
            AS
            BEGIN
                INSERT INTO auditoria_log (tabla, operacion, usuario, fecha_hora, datos)
                SELECT '{tabla}', 'UPDATE', SYSTEM_USER, GETDATE(), 
                       (SELECT * FROM deleted FOR JSON PATH) + ' -> ' + (SELECT * FROM inserted FOR JSON PATH)
            END
            """,
            'delete': f"""
            CREATE TRIGGER tr_{tabla}_delete ON {tabla}
            AFTER DELETE
            AS
            BEGIN
                INSERT INTO auditoria_log (tabla, operacion, usuario, fecha_hora, datos)
                SELECT '{tabla}', 'DELETE', SYSTEM_USER, GETDATE(), (SELECT * FROM deleted FOR JSON PATH)
            END
            """
        }

        with self.engine.connect() as conn:
            for trigger_type, trigger_sql in triggers.items():
                try:
                    conn.execute(text(f"DROP TRIGGER IF EXISTS tr_{tabla}_{trigger_type}"))
                    conn.execute(text(trigger_sql))
                except Exception as e:
                    print(f"Error al crear trigger {trigger_type} para {tabla}: {str(e)}")
