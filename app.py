from flask import Flask
from flask_cors import CORS
from api.routes import routes
from alerts.scheduler import start

app = Flask(__name__)
CORS(app)

app.register_blueprint(routes)
start()

app.run(debug=True)
