from flask import Flask, redirect, url_for
from flask_cors import CORS
from config import config
from app.models import db
import os

def create_app(config_name='development'):
    """Application factory"""
    app = Flask(__name__)

    # Load config
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    CORS(app)

    # Create upload folder
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['FAISS_INDEX_PATH'], exist_ok=True)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.cases import cases_bp
    try:
        from app.routes.documents import documents_bp, upload_document
        documents_available = True
    except ImportError:
        documents_available = False
        print("⚠️  PyMuPDF not installed - Document upload (F5) disabled")

    from app.routes.ai_assistant import ai_bp
    from app.routes.deadlines import deadlines_bp
    from app.routes.risk import risk_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(cases_bp, url_prefix='/cases')
    if documents_available:
        app.register_blueprint(documents_bp, url_prefix='/documents')
        app.add_url_rule('/upload', endpoint='root_upload', view_func=upload_document, methods=['POST'])
    app.register_blueprint(ai_bp, url_prefix='/ai')
    app.register_blueprint(deadlines_bp, url_prefix='/deadlines')
    app.register_blueprint(risk_bp, url_prefix='/risk')

    # Create tables
    with app.app_context():
        from app.services.auth_service import seed_state_bar_council_records
        db.create_all()
        seed_state_bar_council_records()

    @app.route('/')
    def index():
        return redirect(url_for('cases.dashboard'))

    return app
