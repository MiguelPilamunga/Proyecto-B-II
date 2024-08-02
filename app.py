from flask import Flask
from flask_cors import CORS

from routes.AuditRoute import auditoria
from routes.MetodosGenericos import integridad

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": ["http://localhost:4200", "http://localhost:3000"]}})

app.register_blueprint(integridad)
app.register_blueprint(auditoria)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)