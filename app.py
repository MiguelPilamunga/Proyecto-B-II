from flask import Flask, jsonify, request
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv
import os
import traceback
from sqlalchemy.exc import SQLAlchemyError
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)

def create_database_engine(server, database, username, password, port):
    connection_string = f"mssql+pymssql://{username}:{password}@{server}:{port}/{database}"
    return create_engine(connection_string)

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
            return {'table': tabla_hija, 'referred_table': tabla_padre, 'foreign_key': None, 'result': None}

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
            columns = result.keys()
            result_data = [dict(zip(columns, row)) for row in registros_huerfanos]
            return {'table': tabla_hija, 'referred_table': tabla_padre, 'foreign_key': fk_column, 'result': result_data}
        else:
            return {'table': tabla_hija, 'referred_table': tabla_padre, 'foreign_key': fk_column, 'result': None}

    except SQLAlchemyError as e:
        print(f"Error al verificar la integridad referencial: {str(e)}")
        return {'table': tabla_hija, 'referred_table': tabla_padre, 'foreign_key': None, 'result': str(e)}

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/test-db', methods=['POST'])
def test_db():
    try:
        data = request.json
        server = data.get('server')
        database = data.get('database')
        username = data.get('username')
        password = data.get('password')
        port = data.get('port')
        
        engine = create_database_engine(server, database, username, password, port)
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        table_data = {}
        integrity_results = []

        for table in tables:
            # Get table records
            query = text(f"SELECT * FROM {table}")
            with engine.connect() as connection:
                result = connection.execute(query)
                columns = result.keys()
                records = result.fetchall()
                table_data[table] = [dict(zip(columns, record)) for record in records]
            
            # Check for referential integrity anomalies
            foreign_keys = inspector.get_foreign_keys(table)
            for fk in foreign_keys:
                referred_table = fk['referred_table']
                if referred_table in tables:
                    result = verificar_integridad_referencial(engine, table, referred_table)
                    if result['result']:
                        integrity_results.append(result)

        return jsonify({
            'table_data': table_data,
            'integrity_results': integrity_results
        })
    except Exception as e:
        # Print error details for debugging
        print("Error details:", traceback.format_exc())
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
