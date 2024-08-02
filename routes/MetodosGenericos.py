from flask import Blueprint, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

from services.IntegridadService import IntegridadReferencialService

integridad = Blueprint('integridad', __name__, url_prefix='/integridad')

def validate_connection_params(server, database, username, password):
    if any(param is None or param.strip() == '' for param in [server, database, username, password]):
        return False
    return True

@integridad.route('/check', methods=['POST'])
def check_integrity():
    server = request.form.get('server')
    database = request.form.get('database')
    username = request.form.get('username')
    password = request.form.get('password')

    if not validate_connection_params(server, database, username, password):
        return jsonify({
            "status": "error",
            "message": "Faltan datos de conexión o algunos datos son inválidos.",
            "resultados": {}
        }), 400

    connection_string = f"mssql+pymssql://{username}:{password}@{server}/{database}"
    print(f"Cadena de conexión: {connection_string}") 
    
    
    try:
        engine = create_engine(connection_string)
        servicio = IntegridadReferencialService(engine)

        resultados = servicio.run_all_checks()

        violation_summary = []
        total_violations = 0

        for check_name, result in resultados.items():
            if isinstance(result, list) and result:
                total_violations += len(result)
                violation_summary.append(resultados.get(f"{check_name}_explanation", ""))

        status = "warning" if total_violations > 0 else "success"
        message = "Se encontraron violaciones de integridad referencial" if total_violations > 0 else "La integridad referencial está intacta"

        return jsonify({
            "status": status,
            "message": message,
            "total_violations": total_violations,
            "violation_summary": violation_summary,
            "detailed_results": resultados
        }), 200

    except SQLAlchemyError as e:
        return jsonify({
            "status": "error",
            "message": f"Error de base de datos: {str(e)}",
            "resultados": {}
        }), 500


@integridad.route('/count_violations', methods=['POST'])
def count_integrity_violations():
    server = request.form.get('server')
    database = request.form.get('database')
    username = request.form.get('username')
    password = request.form.get('password')

    connection_string = f"mssql+pymssql://{username}:{password}@{server}/{database}"

    try:
        engine = create_engine(connection_string)
        servicio = IntegridadReferencialService(engine)

        resultados = servicio.run_all_checks()

        violations_count = {k: len(v) for k, v in resultados.items() if not v.empty}
        total_violations = sum(violations_count.values())

        return jsonify({
            "status": "success",
            "message": "Conteo de violaciones de integridad referencial",
            "total_violations": total_violations,
            "violations_details": violations_count
        }), 200

    except SQLAlchemyError as e:
        return jsonify({
            "status": "error",
            "message": f"Error de base de datos: {str(e)}",
            "total_violations": 0
        }), 500