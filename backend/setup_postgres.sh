#!/bin/bash
# Script de configuration PostgreSQL pour l'application FAQ-IA

echo "🔧 Configuration PostgreSQL pour FAQ-IA..."

# 1. Créer la base de données si elle n'existe pas
echo "📋 Création de la base de données faq_ia..."
sudo -u postgres createdb faq_ia 2>/dev/null || echo "Base de données faq_ia existe déjà"

# 2. Configurer l'authentification PostgreSQL
echo "🔐 Configuration de l'authentification..."

# Option 1: Configurer avec mot de passe
echo "Voulez-vous configurer un mot de passe pour PostgreSQL ? (o/n)"
read -r setup_password

if [[ $setup_password == "o" || $setup_password == "O" ]]; then
    echo "Entrez le mot de passe pour l'utilisateur postgres:"
    sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"
    echo "Mot de passe configuré : 'postgres'"

    # Mettre à jour la configuration de l'application
    echo "🔄 Mise à jour de la configuration..."
    export DB_PASSWORD="postgres"

else
    # Option 2: Configurer l'authentification trust pour les connexions locales
    echo "🔓 Configuration de l'authentification trust pour les connexions locales..."

    # Sauvegarder le fichier pg_hba.conf original
    sudo cp /etc/postgresql/*/main/pg_hba.conf /etc/postgresql/*/main/pg_hba.conf.backup

    # Modifier temporairement pg_hba.conf pour autoriser les connexions locales
    sudo sed -i 's/local   all             postgres                                peer/local   all             postgres                                trust/' /etc/postgresql/*/main/pg_hba.conf
    sudo sed -i 's/local   all             all                                     peer/local   all             all                                     trust/' /etc/postgresql/*/main/pg_hba.conf

    # Redémarrer PostgreSQL pour appliquer les changements
    sudo systemctl restart postgresql

    echo "✅ Configuration trust appliquée pour les connexions locales"
fi

echo "🎉 Configuration PostgreSQL terminée!"
echo "Vous pouvez maintenant lancer: python3 init_db.py"
