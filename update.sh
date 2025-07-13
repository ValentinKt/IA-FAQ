#!/bin/bash

# Script de mise à jour pour FAQ-IA
# Usage: sudo ./update.sh

set -e

APP_NAME="faq-ia"
APP_DIR="/var/www/$APP_NAME"

echo "🔄 Mise à jour de FAQ-IA..."

# Vérifier les privilèges root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Ce script doit être exécuté avec les privilèges root (sudo)"
    exit 1
fi

echo "⏹️  Arrêt de l'application..."
systemctl stop $APP_NAME

echo "📁 Sauvegarde de l'ancienne version..."
cp -r $APP_DIR $APP_DIR.backup.$(date +%Y%m%d_%H%M%S)

echo "📦 Mise à jour des fichiers..."
cp -r backend/* $APP_DIR/backend/
cp -r frontend/* $APP_DIR/frontend/ 2>/dev/null || echo "⚠️  Pas de frontend à mettre à jour"

echo "🐍 Mise à jour des dépendances Python..."
cd $APP_DIR/backend
source venv/bin/activate
pip install -r requirements.txt

echo "🔧 Restauration des permissions..."
chown -R www-data:www-data $APP_DIR

echo "🗄️  Mise à jour de la base de données..."
sudo -u www-data bash -c "cd $APP_DIR/backend && source venv/bin/activate && alembic upgrade head" || echo "⚠️  Pas de migrations à appliquer"

echo "🚀 Redémarrage de l'application..."
systemctl start $APP_NAME
systemctl reload nginx

echo "✅ Mise à jour terminée !"
systemctl status $APP_NAME --no-pager -l
