#!/bin/bash

# Script pour récupérer la dernière version depuis deploy/nginx-config
# Usage: ./pull_latest.sh

set -e

echo "🔄 Récupération de la dernière version depuis deploy/nginx-config..."

# Vérifier si nous sommes dans un repository Git
if [ ! -d ".git" ]; then
    echo "❌ Ce répertoire n'est pas un repository Git."
    echo "💡 Si c'est un nouveau serveur, utilisez :"
    echo "   git clone -b deploy/nginx-config https://github.com/FOXEST57/faq-IA.git"
    exit 1
fi

# Sauvegarder les modifications locales si il y en a
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Des modifications locales détectées. Sauvegarde..."
    git stash push -m "Sauvegarde automatique avant mise à jour $(date)"
    echo "✅ Modifications sauvegardées avec git stash"
fi

# Récupérer les dernières modifications
echo "📥 Récupération des dernières modifications..."
git fetch origin

# Vérifier sur quelle branche nous sommes
CURRENT_BRANCH=$(git branch --show-current)
echo "📍 Branche actuelle: $CURRENT_BRANCH"

if [ "$CURRENT_BRANCH" != "deploy/nginx-config" ]; then
    echo "🔄 Basculement vers la branche deploy/nginx-config..."
    git checkout deploy/nginx-config
fi

# Mettre à jour avec la dernière version
echo "⬇️  Mise à jour vers la dernière version..."
git pull origin deploy/nginx-config

echo "✅ Récupération terminée !"
echo ""
echo "📋 Prochaines étapes recommandées :"
echo "   1. Vérifier les nouveaux fichiers: ls -la"
echo "   2. Si l'app est déjà installée: sudo ./update.sh"
echo "   3. Si première installation: sudo ./deploy.sh"
echo ""
echo "🔧 Pour voir les modifications récupérées :"
echo "   git log --oneline -5"
