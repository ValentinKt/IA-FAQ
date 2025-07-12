from flask import request, g
from models import db, VisitLog
from datetime import datetime
import logging

def log_visit():
    """Enregistre la visite actuelle dans la base de données"""
    try:
        # Récupérer l'IP du visiteur (gestion des proxies)
        if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
            ip_address = request.environ['REMOTE_ADDR']
        else:
            ip_address = request.environ['HTTP_X_FORWARDED_FOR']

        # Récupérer l'URL complète
        url = request.url

        # Créer l'entrée de log
        visit = VisitLog(
            ip_address=ip_address,
            url=url,
            timestamp=datetime.utcnow()
        )

        db.session.add(visit)
        db.session.commit()

    except Exception as e:
        # En cas d'erreur, on ne veut pas casser l'application
        logging.error(f"Erreur lors de l'enregistrement de la visite: {e}")
        db.session.rollback()

def setup_visit_logging(app):
    """Configure la journalisation des visites pour l'application Flask"""

    @app.before_request
    def before_request():
        # Ignorer les requêtes statiques et certaines routes
        ignored_paths = ['/static/', '/favicon.ico', '/robots.txt']
        ignored_extensions = ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg']

        # Vérifier si l'URL doit être ignorée
        for path in ignored_paths:
            if request.path.startswith(path):
                return

        for ext in ignored_extensions:
            if request.path.endswith(ext):
                return

        # Enregistrer la visite
        log_visit()
