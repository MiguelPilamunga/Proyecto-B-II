from flask import Blueprint, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

from services.IntegridadService import get_integrity_violations

integridad = Blueprint('integridad', __name__, url_prefix='/integridad')



@integridad.route('/check', methods=['POST'])
def check_integrity():
    server = request.form.get('server')
    database = request.form.get('database')
    username = request.form.get('username')
    password = request.form.get('password')
    tabla_hija = request.form.get('tabla_hija')
    tabla_padre = request.form.get('tabla_padre')

    connection_string = f"mssql+pymssql://{username}:{password}@{server}/{database}"

    try:
        engine = create_engine(connection_string)
        violations = get_integrity_violations(engine, tabla_hija, tabla_padre)

        if not violations:
            return jsonify({
                "status": "error",
                "message": f"No se encontró una clave foránea de {tabla_hija} a {tabla_padre}",
                "violations": {}
            }), 400

        total_violations = sum(v["total_violations"] for v in violations.values())

        if total_violations > 0:
            return jsonify({
                "status": "warning",
                "message": f"Se encontraron violaciones de integridad referencial entre '{tabla_hija}' y '{tabla_padre}'",
                "violations": violations,
                "total_violations": total_violations
            }), 200
        else:
            return jsonify({
                "status": "success",
                "message": f"La integridad referencial entre {tabla_hija} y {tabla_padre} está intacta.",
                "violations": violations,
                "total_violations": 0
            }), 200

    except SQLAlchemyError as e:
        return jsonify({
            "status": "error",
            "message": f"Error de base de datos: {str(e)}",
            "violations": {}
        }), 500

@integridad.route('/count_violations', methods=['POST'])
def count_integrity_violations():
    server = request.form.get('server')
    database = request.form.get('database')
    username = request.form.get('username')
    password = request.form.get('password')
    tabla_hija = request.form.get('tabla_hija')
    tabla_padre = request.form.get('tabla_padre')

    connection_string = f"mssql+pymssql://{username}:{password}@{server}/{database}"

    try:
        engine = create_engine(connection_string)
        violations = get_integrity_violations(engine, tabla_hija, tabla_padre)

        if not violations:
            return jsonify({
                "status": "error",
                "message": f"No se encontró una clave foránea de {tabla_hija} a {tabla_padre}",
                "total_violations": 0
            }), 400

        total_violations = sum(v["total_violations"] for v in violations.values())

        return jsonify({
            "status": "success",
            "message": f"Conteo de violaciones de integridad referencial entre {tabla_hija} y {tabla_padre}",
            "total_violations": total_violations,
            "violations_details": violations
        }), 200

    except SQLAlchemyError as e:
        return jsonify({
            "status": "error",
            "message": f"Error de base de datos: {str(e)}",
            "total_violations": 0
        }), 500