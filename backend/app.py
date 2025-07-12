from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from view.main import main_bp
from view.auth import auth_bp
from view.admin import admin_bp
from view.faq import faq_bp
from view.pdf import pdf_bp
from view.analytics import analytics_bp
from models import db
from config import config
from utils.visit_logger import setup_visit_logging
import os

def create_app(config_name=None):
    """Factory pour créer l'application Flask"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'production')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)

    # Configuration de la journalisation des visites
    setup_visit_logging(app)

    # Filtre Jinja2 personnalisé pour convertir les sauts de ligne en <br>
    @app.template_filter('nl2br')
    def nl2br_filter(text):
        """Convertit les sauts de ligne en balises <br>"""
        if text is None:
            return ''
        return text.replace('\n', '<br>\n')

    # Enregistrement de tous les blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(faq_bp)
    app.register_blueprint(pdf_bp)
    app.register_blueprint(analytics_bp)

    app.secret_key = app.config.get('SECRET_KEY', 'dev')

    return app

# Pour compatibilité avec Gunicorn
app = create_app()
