import sqlalchemy
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

engine = sqlalchemy.create_engine("mssql+pymssql://sa:password123@localhost:1433/master")

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT @@version;"))
        version = result.scalar()
    print(f"Conexión exitosa. Versión de SQL Server: {version}")
except SQLAlchemyError as e:
    print(f"Error al conectar a la base de datos: {str(e)}")