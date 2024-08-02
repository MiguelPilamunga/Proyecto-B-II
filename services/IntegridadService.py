from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
def get_integrity_violations(engine, tabla_hija, tabla_padre):
    inspector = inspect(engine)
    foreign_keys = inspector.get_foreign_keys(tabla_hija)
    violations = {}

    for fk in foreign_keys:
        if fk['referred_table'] == tabla_padre:
            fk_column = fk['constrained_columns'][0]
            referred_column = fk['referred_columns'][0]

            # Verificar registros huérfanos
            query_orphans = text(f"""
            SELECT COUNT(*) 
            FROM {tabla_hija} h
            LEFT JOIN {tabla_padre} p ON h.{fk_column} = p.{referred_column}
            WHERE p.{referred_column} IS NULL AND h.{fk_column} IS NOT NULL
            """)

            # Verificar valores nulos (si la FK no permite nulos)
            query_nulls = text(f"""
            SELECT COUNT(*) 
            FROM {tabla_hija}
            WHERE {fk_column} IS NULL
            """)

            with engine.connect() as connection:
                orphans_count = connection.execute(query_orphans).scalar()
                nulls_count = connection.execute(query_nulls).scalar()

            violations[fk_column] = {
                "orphaned_records": orphans_count,
                "null_values": nulls_count,
                "total_violations": orphans_count + nulls_count
            }

    return violations