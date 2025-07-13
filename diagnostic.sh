#!/bin/bash

# Script de diagnostic pour FAQ-IA
# Usage: ./diagnostic.sh

echo "🔍 Diagnostic de l'application FAQ-IA"
echo "======================================"

# Vérifier le service systemd
echo ""
echo "📋 Statut du service systemd:"
systemctl is-active faq-ia.service --quiet && echo "✅ Service actif" || echo "❌ Service inactif"
systemctl is-enabled faq-ia.service --quiet && echo "✅ Service activé au démarrage" || echo "❌ Service non activé au démarrage"

# Vérifier les processus Gunicorn
echo ""
echo "🔄 Processus Gunicorn:"
GUNICORN_PROCS=$(pgrep -f "gunicorn.*app:app" | wc -l)
if [ $GUNICORN_PROCS -gt 0 ]; then
    echo "✅ $GUNICORN_PROCS processus Gunicorn en cours"
    ps aux | grep -E "gunicorn.*app:app" | grep -v grep
else
    echo "❌ Aucun processus Gunicorn trouvé"
fi

# Vérifier l'environnement virtuel
echo ""
echo "🐍 Environnement virtuel:"
VENV_PATH="/var/www/html/faq-IA/backend/venv"
if [ -f "$VENV_PATH/bin/python" ]; then
    echo "✅ Environnement virtuel présent"
    echo "   Python: $($VENV_PATH/bin/python --version)"

    if [ -f "$VENV_PATH/bin/gunicorn" ]; then
        echo "✅ Gunicorn installé: $($VENV_PATH/bin/gunicorn --version)"
    else
        echo "❌ Gunicorn non trouvé dans l'environnement virtuel"
    fi
else
    echo "❌ Environnement virtuel non trouvé"
fi

# Vérifier les ports
echo ""
echo "🌐 Ports d'écoute:"
if netstat -tlnp 2>/dev/null | grep ":8000" > /dev/null; then
    echo "✅ Port 8000 en écoute:"
    netstat -tlnp | grep ":8000"
else
    echo "❌ Port 8000 non en écoute"
fi

if netstat -tlnp 2>/dev/null | grep ":80" > /dev/null; then
    echo "✅ Port 80 (nginx) en écoute:"
    netstat -tlnp | grep ":80"
else
    echo "❌ Port 80 (nginx) non en écoute"
fi

# Test de l'API
echo ""
echo "🧪 Test de l'application:"
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ Application répond sur localhost:8000"
    echo "   Page d'accueil accessible"
else
    echo "❌ Application ne répond pas sur localhost:8000"
fi

# Test des routes API
if curl -s http://localhost:8000/faq > /dev/null 2>&1; then
    echo "✅ Route FAQ accessible"
else
    echo "❌ Route FAQ non accessible"
fi

# Vérifier les logs récents
echo ""
echo "📄 Dernières lignes des logs (5 dernières):"
journalctl -u faq-ia.service --no-pager -n 5

# Vérifier l'espace disque
echo ""
echo "💾 Espace disque:"
df -h /var/www/html/faq-IA

echo ""
echo "🔧 Commandes utiles pour le dépannage:"
echo "   - Logs en temps réel: journalctl -u faq-ia.service -f"
echo "   - Redémarrer service: sudo systemctl restart faq-ia.service"
echo "   - Recharger config: sudo systemctl daemon-reload"
echo "   - Vérifier nginx: sudo nginx -t"
