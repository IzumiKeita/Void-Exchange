from flask import Flask, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv  # Cargar variables de entorno locales
from backend.extensions import db

# Cargar .env si existe (para desarrollo local)
load_dotenv()

# Importar Blueprints
from backend.controllers.monitor_controller import monitor_bp
from backend.controllers.items_controller import items_bp
from backend.controllers.trends_controller import trends_bp
from backend.controllers.ducats_controller import ducats_bp
from backend.controllers.vault_controller import vault_bp
from backend.controllers.analysis_controller import analysis_bp
from backend.controllers.ai_controller import ai_bp
from backend.controllers.void_trader_controller import void_trader_bp

import sys

def create_app():
    # Configuración para servir Frontend estático (Vue.js) desde Flask
    # Detectar si estamos ejecutando en modo "congelado" (PyInstaller)
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
        # En el ejecutable, empaquetaremos 'dist' en la raíz temporal
        dist_folder = os.path.join(base_path, 'dist')
        # La base de datos debe persistir junto al ejecutable, no en la carpeta temporal
        db_folder = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.dirname(__file__))
        dist_folder = os.path.join(base_path, 'frontend', 'dist')
        db_folder = os.path.join(base_path, 'data')

    app = Flask(__name__, static_folder=dist_folder, static_url_path='')
    
    # Configuración de Base de Datos
    # Prioridad: 1. Variable de entorno (Render/Postgres) 2. SQLite local
    os.makedirs(db_folder, exist_ok=True)
    db_path = os.path.join(db_folder, 'market.db')
    
    # Windows path fix for sqlite
    db_uri = os.environ.get('DATABASE_URL')
    if db_uri and db_uri.startswith("postgres://"):
        db_uri = db_uri.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri or f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializar SQLAlchemy
    db.init_app(app)

    # Configuración de CORS
    CORS(app)
    
    # Registro de Blueprints
    app.register_blueprint(monitor_bp)
    app.register_blueprint(items_bp)
    app.register_blueprint(trends_bp)
    app.register_blueprint(ducats_bp)
    app.register_blueprint(vault_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(void_trader_bp)

    # Crear tablas si no existen (dentro del contexto de la app)
    with app.app_context():
        # Importar modelos para que SQLAlchemy los conozca
        from backend import models
        db.create_all()

    @app.route('/health')
    def health():
        return "OK", 200

    # Servir Frontend en producción
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')
    
    return app
