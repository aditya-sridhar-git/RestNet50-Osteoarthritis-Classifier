from flask import Flask
from flask_cors import CORS
from api.routes import routes
from alerts.scheduler import start

app = Flask(__name__)
CORS(app)

app.register_blueprint(routes)
start()

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
