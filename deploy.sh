#!/bin/bash

# Script de déploiement pour FAQ-IA sur Debian avec Gunicorn
# Usage: sudo ./deploy.sh

set -e

echo "🚀 Déploiement de FAQ-IA sur Debian..."

# Variables
APP_NAME="faq-ia"
APP_USER="www-data"
APP_GROUP="www-data"
APP_DIR="/var/www/$APP_NAME"
SERVICE_FILE="/etc/systemd/system/$APP_NAME.service"
NGINX_SITE="/etc/nginx/sites-available/$APP_NAME"
NGINX_ENABLED="/etc/nginx/sites-enabled/$APP_NAME"
LOG_DIR="/var/log/$APP_NAME"
RUN_DIR="/var/run/$APP_NAME"

# Vérifier les privilèges root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Ce script doit être exécuté avec les privilèges root (sudo)"
    exit 1
fi

echo "📦 Installation des dépendances système..."
apt update
apt install -y python3 python3-pip python3-venv nginx supervisor

echo "📂 Création des répertoires..."
mkdir -p $APP_DIR
mkdir -p $LOG_DIR
mkdir -p $RUN_DIR
chown $APP_USER:$APP_GROUP $LOG_DIR
chown $APP_USER:$APP_GROUP $RUN_DIR

echo "📁 Copie des fichiers d'application..."
cp -r backend/ $APP_DIR/
cp -r frontend/ $APP_DIR/ 2>/dev/null || echo "⚠️  Dossier frontend non trouvé, ignoré"

echo "🐍 Configuration de l'environnement Python..."
cd $APP_DIR/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "🔧 Configuration des permissions..."
chown -R $APP_USER:$APP_GROUP $APP_DIR
chmod +x $APP_DIR/backend/start.sh

echo "📋 Installation du service systemd..."
cp $APP_NAME.service $SERVICE_FILE
systemctl daemon-reload
systemctl enable $APP_NAME

echo "🌐 Configuration de Nginx..."
cp nginx.conf $NGINX_SITE
ln -sf $NGINX_SITE $NGINX_ENABLED
nginx -t

echo "🗄️  Initialisation de la base de données..."
cd $APP_DIR/backend
sudo -u $APP_USER bash -c "source venv/bin/activate && python -c \"
from app import app, db
with app.app_context():
    db.create_all()
    print('Base de données initialisée !')
\""

echo "🔄 Démarrage des services..."
systemctl start $APP_NAME
systemctl reload nginx

echo "✅ Déploiement terminé !"
echo ""
echo "🎉 Votre application FAQ-IA est maintenant accessible :"
echo "   URL: http://cd2ia-thomas.stagiairesmns.fr"
echo ""
echo "📊 Commandes utiles :"
echo "   - Statut du service: systemctl status $APP_NAME"
echo "   - Logs en temps réel: journalctl -fu $APP_NAME"
echo "   - Redémarrer l'app: systemctl restart $APP_NAME"
echo "   - Logs nginx: tail -f /var/log/nginx/$APP_NAME*.log"
echo ""
echo "🔧 Pour mettre à jour l'application :"
echo "   1. Copiez les nouveaux fichiers dans $APP_DIR"
echo "   2. Redémarrez: systemctl restart $APP_NAME"
