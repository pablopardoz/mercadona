import os
import sys
import logging
import traceback
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from database import init_pool

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

print("Inicializando base de datos...")
init_pool()
print("Base de datos lista.")


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    stream=sys.stdout,
)


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

    @app.errorhandler(500)
    def handle_500(e):
        logging.error("Error 500 interno:\n%s", traceback.format_exc())
        return jsonify({'error': 'Error interno del servidor', 'detalle': str(e)}), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        logging.error("Excepción no controlada:\n%s", traceback.format_exc())
        return jsonify({'error': 'Error interno del servidor', 'detalle': str(e)}), 500

    @app.route('/api/health')
    def health():
        return {'status': 'ok'}

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
