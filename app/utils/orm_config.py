import sqlalchemy
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError

def verificar_integridad_referencial(engine, tabla_hija, tabla_padre):
    try:
        inspector = inspect(engine)
        
        # Detectar la clave foránea
        foreign_keys = inspector.get_foreign_keys(tabla_hija)
        fk_column = None
        for fk in foreign_keys:
            if fk['referred_table'] == tabla_padre:
                fk_column = fk['constrained_columns'][0]
                break
        
        if not fk_column:
            print(f"No se encontró una clave foránea de {tabla_hija} a {tabla_padre}")
            return None

        query = text(f"""
        SELECT h.*
        FROM {tabla_hija} h
        LEFT JOIN {tabla_padre} p ON h.{fk_column} = p.id
        WHERE p.id IS NULL
        """)

        with engine.connect() as connection:
            result = connection.execute(query)
            registros_huerfanos = result.fetchall()

        if registros_huerfanos:
            print(f"Se encontraron registros en '{tabla_hija}' sin correspondencia en '{tabla_padre}':")
            for registro in registros_huerfanos:
                print(f"ID en {tabla_hija}: {registro[0]}, {fk_column}: {registro._mapping[fk_column]}")
            return False
        else:
            print(f"La integridad referencial entre {tabla_hija} y {tabla_padre} está intacta.")
            return True

    except SQLAlchemyError as e:
        print(f"Error al verificar la integridad referencial: {str(e)}")
        return None