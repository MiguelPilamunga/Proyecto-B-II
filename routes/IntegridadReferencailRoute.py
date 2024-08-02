# routes/IntegridadReferencialRoute.py

from flask import Blueprint, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from services.IntegridadReferencialService import check_integridad_referencial

integridad_referencial = Blueprint('integridad_referencial', __name__, url_prefix='/integridad_referencialgi')

def get_connection_string(request):
    server = request.form.get('server')
    database = request.form.get('database')
    username = request.form.get('username')
    password = request.form.get('password')
    return f"mssql+pymssql://{username}:{password}@{server}/{database}"

@integridad_referencial.route('/check', methods=['POST'])
def check_integridad():
    connection_string = get_connection_string(request)

    try:
        engine = create_engine(connection_string)
        result, error = check_integridad_referencial(engine)
        if error:
            return jsonify({"status": "error", "message": error}), 500
        return jsonify({
            "status": "success",
            "resultado": result
        }), 200
    except SQLAlchemyError as e:
        return jsonify({"status": "error", "message": str(e)}), 500