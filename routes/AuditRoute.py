from flask import Blueprint, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

from Models.AuditModel import AuditModel
from services.DataAnomaly import check_data_anomalies

auditoria = Blueprint('auditoria', __name__, url_prefix='/auditoria')

def get_connection_string(request):
    server = request.form.get('server')
    database = request.form.get('database')
    username = request.form.get('username')
    password = request.form.get('password')
    return f"mssql+pymssql://{username}:{password}@{server}/{database}"

@auditoria.route('/auditar', methods=['POST'])
def auditar_operacion():
    server = request.form.get('server')
    database = request.form.get('database')
    username = request.form.get('username')
    password = request.form.get('password')
    query = request.form.get('query')

    if not all([server, database, username, password, query]):
        return jsonify({"status": "error", "message": "Faltan parámetros en la solicitud"}), 400

    try:
        servicio = AuditModel(server, database, username, password)
        resultado = servicio.auditar_operacion(query)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error al auditar operación: {str(e)}"}), 500


@auditoria.route('/logs', methods=['POST'])
def obtener_logs_auditoria():
    connection_string = get_connection_string(request)
    tabla = request.form.get('tabla')
    operacion = request.form.get('operacion')
    fecha_inicio = request.form.get('fecha_inicio')
    fecha_fin = request.form.get('fecha_fin')

    try:
        engine = create_engine(connection_string)
        servicio = AuditModel(engine)

        if fecha_inicio:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        if fecha_fin:
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')

        logs = servicio.obtener_logs_auditoria(tabla, operacion, fecha_inicio, fecha_fin)
        return jsonify({"status": "success", "logs": logs}), 200
    except SQLAlchemyError as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@auditoria.route('/check_anomalies', methods=['POST'])
def check_anomalies():
    connection_string = get_connection_string(request)

    try:
        engine = create_engine(connection_string)
        anomalies = check_data_anomalies(engine)
        return jsonify({"status": "success", "anomalies": anomalies}), 200
    except SQLAlchemyError as e:
        return jsonify({"status": "error", "message": str(e)}), 500