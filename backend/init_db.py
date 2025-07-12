#!/usr/bin/env python3
"""
Script d'initialisation de la base de données PostgreSQL
Lance ce script après avoir déployé l'application pour créer les tables
"""

import os
import sys
from pathlib import Path

# Ajouter le dossier backend au path Python
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from app import create_app
from models import db

def init_database():
    """Initialise la base de données PostgreSQL"""
    print("🔄 Initialisation de la base de données PostgreSQL...")

    # Créer l'application avec la configuration de production
    app = create_app('production')

    with app.app_context():
        try:
            # Test de connexion d'abord
            print("🔍 Test de connexion à PostgreSQL...")
            db.engine.connect()
            print("✅ Connexion PostgreSQL réussie!")

            # Créer toutes les tables
            print("📋 Création des tables...")
            db.create_all()
            print("✅ Tables créées avec succès!")

            # Vérifier les tables créées
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()

            if tables:
                print(f"📋 Tables créées: {', '.join(tables)}")
            else:
                print("⚠️  Aucune table trouvée - vérifiez vos modèles")

        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation: {e}")

            # Suggestions d'aide selon le type d'erreur
            error_str = str(e)
            if "password" in error_str.lower():
                print("\n💡 Solutions possibles:")
                print("1. Configurer l'authentification PostgreSQL:")
                print("   sudo -u postgres psql")
                print("   ALTER USER postgres PASSWORD 'votre_mot_de_passe';")
                print("   \\q")
                print("2. Ou modifier pg_hba.conf pour autoriser les connexions locales sans mot de passe")
            elif "database" in error_str.lower() and "does not exist" in error_str.lower():
                print("\n💡 Créer la base de données:")
                print("   sudo -u postgres createdb faq_ia")
            elif "connection" in error_str.lower():
                print("\n💡 Vérifier que PostgreSQL est démarré:")
                print("   sudo systemctl status postgresql")
                print("   sudo systemctl start postgresql")

            return False

    return True

if __name__ == "__main__":
    success = init_database()
    if success:
        print("\n🎉 Base de données initialisée avec succès!")
        print("Vous pouvez maintenant redémarrer Gunicorn:")
        print("sudo systemctl restart faq-ia.service")
    else:
        print("\n💥 Échec de l'initialisation de la base de données.")
        print("Consultez les messages d'erreur ci-dessus pour résoudre le problème.")
        sys.exit(1)
