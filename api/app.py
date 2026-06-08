import os
import sys
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from config import Config
from database import init_pool

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

print("Inicializando base de datos...")
init_pool()
print("Base de datos lista.")


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    from auth import bp as auth_bp
    from tickets import bp as tickets_bp
    from stats import bp as stats_bp
    from kpis import bp as kpis_bp
    from upload import bp as upload_bp
    from supermarkets import bp as supermarkets_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(stats_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(kpis_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(supermarkets_bp)

    @app.route('/api/health')
    def health():
        return {'status': 'ok'}

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
