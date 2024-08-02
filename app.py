from flask import Flask
from flask_cors import CORS

from routes.AnomaliasEnDatos import anomalia_en_datos
from routes.IntegridadReferencialRelaciones import auditoria
from routes.IntegridadReferencailRoute import integridad_referencial

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": [
    "http://localhost:4200", 
    "http://localhost:3000",
    "http://localhost:5000",
    "http://localhost:5173"]}})

app.register_blueprint(auditoria)

app.register_blueprint(anomalia_en_datos)
app.register_blueprint(integridad_referencial)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
