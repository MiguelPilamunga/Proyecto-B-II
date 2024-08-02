from flask import Blueprint, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError


auditoria = Blueprint('auditoria', __name__, url_prefix='/integridad_relacional')

def get_connection_string(request):
    server = request.form.get('server')
    database = request.form.get('database')
    username = request.form.get('username')
    password = request.form.get('password')
    return f"mssql+pymssql://{username}:{password}@{server}/{database}"

@auditoria.route('/check', methods=['POST'])
def check_relaciones_referenciales():
    try:
        connection_string = get_connection_string(request)
        engine = create_engine(connection_string)

        from services.IntegridadReferencialRelacionalService import check_relations
        resultado, logs = check_relations(engine)

        return jsonify({"resultado": resultado, "logs": logs}), 200

    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500