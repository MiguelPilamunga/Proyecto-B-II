# routes/AnomaliasEnDatos.py

from flask import Blueprint, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

from services.DataAnomaly import check_data_anomalies

anomalia_en_datos = Blueprint('anomalia_en_datos', __name__, url_prefix='/auditoria')

def get_connection_string(request):
    server = request.form.get('server')
    database = request.form.get('database')
    username = request.form.get('username')
    password = request.form.get('password')
    return f"mssql+pymssql://{username}:{password}@{server}/{database}"

@anomalia_en_datos.route('/check_anomalies', methods=['POST'])
def check_anomalies():
    connection_string = get_connection_string(request)
    print(connection_string)
    try:
        engine = create_engine(connection_string)
        anomalies, logs = check_data_anomalies(engine)
        return jsonify({"status": "success", "anomalies": anomalies}), 200
    except SQLAlchemyError as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@anomalia_en_datos.route('/get_anomaly_logs', methods=['POST'])
def get_anomaly_logs():
    connection_string = get_connection_string(request)

    try:
        engine = create_engine(connection_string)
        _, logs = check_data_anomalies(engine)
        return jsonify({
            "status": "success",
            "logs": logs
        }), 200
    except SQLAlchemyError as e:
        return jsonify({
            "status": "error",
            "logs": str(e)
        }), 500