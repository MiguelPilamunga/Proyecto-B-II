from flask import Flask
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
load_dotenv()

app = Flask(__name__)

server = os.getenv('SQLSERVER_HOST')
database = os.getenv('SQLSERVER_DB')
username = os.getenv('SQLSERVER_USER')
password = os.getenv('SQLSERVER_PASSWORD')
port = os.getenv('SQLSERVER_PORT')


connection_string = "mssql+pymssql://sa:password123@localhost:1433/master"


engine = create_engine(connection_string)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/test-db')
def test_db():
    try:

        print(server, database, username, password, port)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT @@version;"))
            version = result.scalar()
        return f"Conexión exitosa. Versión de SQL Server: {version}"
    except Exception as e:
        return f"Error al conectar a la base de datos: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)