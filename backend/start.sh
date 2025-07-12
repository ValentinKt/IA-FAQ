#!/bin/bash
# Script de démarrage pour l'API Flask avec Gunicorn
set -e

cd "$(dirname "$0")"

# Vérifier si l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo "❌ Environnement virtuel non trouvé. Création..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

export PYTHONPATH=.

# Mode de démarrage (development ou production)
MODE=${1:-development}

if [ "$MODE" = "production" ]; then
    echo "🚀 Démarrage en mode PRODUCTION avec Gunicorn..."
    # Arrêter les processus existants
    pkill -f "gunicorn.*app:app" 2>/dev/null || true

    # Créer les répertoires de logs si nécessaires
    mkdir -p logs

    # Démarrer avec Gunicorn
    exec gunicorn --config gunicorn.conf.py app:app
else
    echo "🛠️  Démarrage en mode DÉVELOPPEMENT avec Flask..."
    # Arrêter les processus sur le port 8000
    fuser -k 8000/tcp 2>/dev/null || true

    # Démarrer en mode développement
    export FLASK_ENV=development
    export FLASK_DEBUG=1
    python app.py
fi
