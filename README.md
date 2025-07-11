# Sujet Projet Faq Assited by IA : FAA

A réaliser en groupe. Attendu :

- Réalisation de l’application
- Rapport de conception
- Soutenance du projet.
- Travail possible en équipe.
- Déploiement.

Sujet de Projet Web : Implémentation d'un Site Web avec FAQ Intelligente et
Administration

## 1. Introduction
Ce projet a pour objectif de développer un site web interactif en Python, intégrant
une section "Foire Aux Questions" (FAQ) intelligente. Cette FAQ affichera des
questions-réponses qui pourront être initialement générées et enrichies par une IA
générative basée sur un modèle RAG (Retrieval Augmented Generation), à partir
d'un corpus de documents PDF décrivant des formations. Un système
d'administration complet permettra de gérer, modifier, supprimer et ajouter
manuellement ces entrées de la FAQ. De plus, des fonctionnalités d'analyse et de
prédiction des visites seront mises en place.
## 2. Objectifs du Projet
Les objectifs principaux de ce projet sont les suivants :

- Développement d'un site web robuste : Créer un site web fonctionnel et intuitif
en utilisant un framework Python (Flask ou Django).
- FAQ Intelligente (RAG) : Implémenter une FAQ dont les réponses sont
initialement générées ou assistées par un modèle RAG entraîné sur des
documents PDF de descriptions de formations. Les utilisateurs consulteront
une liste de questions/réponses prédéfinies.
- Gestion Administrative de la FAQ : Développer une interface d'administration
sécurisée permettant aux administrateurs de créer, modifier, supprimer et
visualiser les entrées de la FAQ (questions/réponses générées ou ajoutées
manuellement).
- Intégration d'Ollama et d'un SML : Utiliser Ollama pour la gestion et l'inférence
du modèle de langage et un Small Language Model (SML) pour l'assistance à
la génération des réponses de la FAQ.
- Analyse et Prédiction des Visites : Mettre en place un système de
journalisation des visites et de création d'un modèle de prédiction des visites
basé sur le Machine Learning.

## 3. Fonctionnalités Détaillées
3.1. Partie Utilisateur (Frontend)

- Page d'accueil : Présentation du site, informations générales.
- Section FAQ :
o Affichage d'une liste de questions/réponses prédéfinies.
o Possibilité de filtrer ou de rechercher parmi les questions/réponses
affichées (recherche textuelle classique sur les questions et réponses
existantes).
- Page de contact.
3.2. Partie Administration (Backend)
- Tableau de bord : Vue d'ensemble de l'activité du site (statistiques de visites,
etc.).
- Gestion des utilisateurs (administrateurs) : Création, modification, suppression
des comptes administrateurs.
- Gestion de la FAQ :
o Ajout manuel : Possibilité d'ajouter manuellement des paires
question/réponse.
o Modification : Modifier des questions et/ou leurs réponses.
o Suppression : Supprimer des entrées de la FAQ.
o Visualisation : Lister toutes les entrées de la FAQ avec leur source
(manuelle ou initialement générée par l'IA).
o Gestion des documents PDF : Interface pour uploader et gérer les
fichiers PDF servant de corpus pour l'IA générative.
o Génération assistée par l'IA : Un module permettra à l'administrateur de
lancer un processus de génération de questions/réponses basé sur les
PDF via l'IA. Les résultats seront ensuite soumis à l'administrateur pour
validation, modification et ajout à la FAQ.
- Gestion des modèles IA : Possibilité de configurer ou de recharger le modèle
de langage utilisé par l'IA.
- Statistiques et Logs :
o Consultation des logs d'accès au site (horodatage, IP, page visitée).
o Consultation des actions effectuées par les administrateurs
(ajout/modification/suppression de FAQ).
3.3. Module d'Intelligence Artificielle (RAG) (pour l'administration)
- Traitement des PDF : Extraction de texte à partir des documents PDF de
descriptions de formations.
- Indexation : Création d'un index vectoriel des connaissances extraites des
PDF.
- Moteur de recherche sémantique : Utilisé côté administration pour identifier les
passages pertinents en fonction de requêtes (ex: pour générer de nouvelles
questions/réponses ou vérifier l'existence de réponses).
- Génération de réponses : Utilisation d'un Small Language Model (SML) via
Ollama pour assister l'administrateur dans la génération de questions et de
réponses cohérentes et pertinentes en se basant sur les passages récupérés.
Cette génération se fera en arrière-plan ou via une interface spécifique pour
les administrateurs, et non directement par les utilisateurs finaux.
- Fine-tuning (optionnel) : Possibilité de fine-tuner le SML sur des données
spécifiques aux formations pour améliorer la pertinence.
3.4. Module d'Analyse et de Prédiction (Machine Learning)
- Journalisation des visites : Enregistrement de chaque visite sur le site (URL,
horodatage, informations de l'utilisateur anonymisées).
- Modèle de prédiction des visites :
o Utilisation de techniques de Machine Learning (e.g., séries temporelles,
régression) pour prédire le nombre de visites futures sur le site.
o Visualisation des prédictions dans le tableau de bord administrateur.

## 4. Requirements Techniques
4.1. Requirements Logiciels

- Système d'exploitation : Linux (Ubuntu/Debian recommandé), macOS, ou
Windows.
- Langage de programmation : Python 3.9+
- Framework Web : Flask ou Django (choix à justifier, Django pour un projet
plus conséquent avec administration intégrée, Flask pour une plus grande
légèreté et personnalisation).
- Base de données : PostgreSQL (recommandé pour la robustesse et les
fonctionnalités), ou SQLite (pour le développement local) ou SQL Server.
- Pour l'IA générative (côté administration) :
o Ollama : Pour exécuter et gérer les modèles de langage locaux.
o Bibliothèques Python pour le traitement du langage naturel (NLP) :
 PyMuPDF ou pdfminer.six pour l'extraction de texte des PDF.
 Langchain ou LlamaIndex pour l'implémentation du RAG
(indexation, recherche, orchestration avec Ollama).
 sentence-transformers pour la génération d'embeddings.
 Un Small Language Model (SML) compatible avec Ollama (ex:
Llama 3 mini, Phi-3, Gemma 2B, Mistral 7B quantisé).
- Pour le Machine Learning :
o scikit-learn pour les algorithmes de prédiction.
o pandas et numpy pour la manipulation de données.
o matplotlib ou seaborn pour la visualisation.
- Pour la gestion des dépendances : pip et venv (environnement virtuel Python).
- Serveur Web : Gunicorn ou uWSGI (pour le déploiement en production avec
Flask/Django).
- Serveur HTTP : Nginx ou Apache (en tant que reverse proxy en production).
4.2. Requirements Infrastructure (pour le déploiement)
- Serveur de développement : Machine locale (ordinateur portable/desktop)
avec une configuration raisonnable (RAM, CPU) pour le développement.
- Serveur de production (minimum) :
o CPU : 2-4 cœurs (selon la charge attendue).
o RAM : 8 Go - 16 Go ou 32Go (essentiel pour Ollama et le modèle de
langage, peut être plus si le SML est conséquent ou si plusieurs
modèles sont chargés).
o Disque : SSD de 50 Go - 100 Go (pour le système d'exploitation, le
code, la base de données et les modèles Ollama qui peuvent être
volumineux).
o Connectivité : Accès Internet stable et port 80/443 ouvert pour le trafic
web.
o GPU (recommandé pour l'inférence rapide du SML) : Une carte
graphique compatible CUDA (NVIDIA) ou ROCm (AMD) avec au moins
4 Go de VRAM (8 Go ou plus est idéal pour des performances
optimales avec certains SML). Si pas de GPU, l'inférence sera plus
lente sur le CPU.
- (En option) Environnement de conteneurisation (recommandé) : Docker et
Docker Compose pour faciliter le déploiement et la gestion des différents
services (application web, base de données, Ollama).

## 5. Étapes de Réalisation (Aperçu)

1. Initialisation du projet : Choix du framework (Flask/Django), configuration de
l'environnement virtuel.
2. Modélisation de la base de données : Définition des modèles pour la FAQ, les
utilisateurs, les logs, etc.
3. Développement du Frontend : Création des interfaces utilisateur (HTML, CSS,
JavaScript).
4. Développement du Backend (API) : Implémentation des vues, routes, gestion
des requêtes.
5. Intégration d'Ollama et du SML (pour l'administration) :
 - Installation d'Ollama.
 - Téléchargement du SML choisi.
 - Implémentation du pipeline RAG (extraction PDF, indexation, recherche, génération assistée pour les administrateurs).
6. Développement du système d'administration : Interfaces CRUD pour la FAQ et,autres entités, y compris le module de génération assistée par l'IA.
7. Mise en place de la journalisation des visites.
8. Développement du module ML pour la prédiction des visites : Collecte dedonnées, entraînement du modèle, intégration.
9. Tests unitaires et d'intégration.
10. Déploiement : Configuration du serveur web, base de données, Ollama, etl'application Python.

## Déploiement avec Nginx

Cette section décrit la configuration complète pour déployer l'application FAQ IA sur un serveur avec nginx et Gunicorn.

### Architecture de déploiement

```
[Client] → [Nginx] → [Gunicorn] → [Flask App]
                ↓
        [React Build (fichiers statiques)]
```

### Configuration Nginx

#### 1. Fichier de configuration nginx (`/etc/nginx/sites-available/ia_faq`)

```nginx
server {
    listen 80;
    server_name cd2ia-thomas.stagiairesmns.fr;

    # Taille maximale pour les uploads
    client_max_body_size 10M;

    # Servir les fichiers statiques du frontend React
    location / {
        try_files $uri $uri/ @backend;
        root /home/tom/Bureau/ia_faq/frontend/build;
        index index.html;
    }

    # Fallback pour les routes React (SPA)
    location @backend {
        try_files $uri /index.html;
        root /home/tom/Bureau/ia_faq/frontend/build;
    }

    # API Backend via Gunicorn
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $server_name;
        
        # Timeout configuration
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    # Servir les fichiers uploads directement
    location /uploads/ {
        alias /home/tom/Bureau/ia_faq/backend/uploads/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Configuration pour les fichiers statiques
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        root /home/tom/Bureau/ia_faq/frontend/build;
    }

    # Logs
    access_log /var/log/nginx/ia_faq_access.log;
    error_log /var/log/nginx/ia_faq_error.log;
}
```

#### 2. Script de démarrage Gunicorn (`start_gunicorn.sh`)

```bash
#!/bin/bash

# Script de démarrage pour Gunicorn
# Usage: ./start_gunicorn.sh

cd /home/tom/Documents/faq-IA/backend

# Activer l'environnement virtuel
source venv/bin/activate

# Démarrer Gunicorn
# (ou utilisez le fichier de config gunicorn.conf.py déjà présent)
gunicorn --config gunicorn.conf.py app:app
```

### Étapes de déploiement

#### 1. Prérequis serveur
```bash
# Installer nginx
sudo apt update
sudo apt install nginx

# Installer Python et pip (si pas déjà fait)
sudo apt install python3 python3-pip python3-venv
```

#### 2. Préparation de l'application

```bash
# Aller dans le dossier backend
cd /home/tom/Documents/faq-IA/backend

# Installer les dépendances (y compris Gunicorn)
pip install -r requirements.txt

# Créer les dossiers de logs
sudo mkdir -p /var/log/gunicorn
sudo mkdir -p /var/log/nginx
sudo chown $USER:$USER /var/log/gunicorn

# Rendre le script Gunicorn exécutable
chmod +x ../start_gunicorn.sh
```

#### 3. Build du frontend

```bash
# Aller dans le dossier frontend
cd /home/tom/Bureau/ia_faq/frontend

# Installer les dépendances Node.js
npm install

# Créer le build de production
npm run build
```

#### 4. Configuration Nginx

```bash
# Copier la configuration nginx
sudo cp /home/tom/Bureau/ia_faq/nginx.conf /etc/nginx/sites-available/ia_faq

# Activer le site
sudo ln -s /etc/nginx/sites-available/ia_faq /etc/nginx/sites-enabled/

# Désactiver le site par défaut (optionnel)
sudo rm /etc/nginx/sites-enabled/default

# Tester la configuration
sudo nginx -t

# Redémarrer nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

#### 5. Démarrage des services

```bash
# Démarrer Gunicorn
cd /home/tom/Bureau/ia_faq
./start_gunicorn.sh

# Vérifier que Gunicorn fonctionne
ps aux | grep gunicorn

# Vérifier les logs
tail -f /var/log/gunicorn/error.log
tail -f /var/log/nginx/ia_faq_error.log
```

### Scripts utiles

#### Arrêter Gunicorn
```bash
pkill -f gunicorn
```

#### Redémarrer l'application
```bash
# Arrêter Gunicorn
pkill -f gunicorn

# Redémarrer Gunicorn
./start_gunicorn.sh

# Recharger nginx
sudo systemctl reload nginx
```

#### Surveillance des logs
```bash
# Logs Gunicorn
tail -f /var/log/gunicorn/access.log
tail -f /var/log/gunicorn/error.log

# Logs Nginx
tail -f /var/log/nginx/ia_faq_access.log
tail -f /var/log/nginx/ia_faq_error.log
```

### Configuration SSL (Optionnel)

Pour activer HTTPS avec Let's Encrypt :

```bash
# Installer Certbot
sudo apt install certbot python3-certbot-nginx

# Obtenir le certificat SSL
sudo certbot --nginx -d cd2ia-thomas.stagiairesmns.fr

# Renouvellement automatique
sudo crontab -e
# Ajouter : 0 12 * * * /usr/bin/certbot renew --quiet
```

### Monitoring et Performance

#### Vérifier le statut des services
```bash
# Status nginx
sudo systemctl status nginx

# Processus Gunicorn
ps aux | grep gunicorn

# Ports utilisés
sudo netstat -tlnp | grep :8000
sudo netstat -tlnp | grep :80
```

#### Optimisations recommandées

1. **Gunicorn Workers** : Ajuster selon CPU disponibles (2 x CPU cores + 1)
2. **Nginx Cache** : Activé pour les fichiers statiques (1 an)
3. **Upload Size** : Configuré à 10MB max
4. **Timeouts** : 300s pour les requêtes longues (IA)

### Troubleshooting

#### Problèmes courants

1. **502 Bad Gateway** : Vérifier que Gunicorn fonctionne sur le port 8000
2. **403 Forbidden** : Vérifier les permissions des dossiers
3. **404 sur API** : Vérifier que les routes Flask sont bien configurées
4. **React routes ne fonctionnent pas** : Vérifier la configuration `@backend`

#### Tests de fonctionnement

```bash
# Test API
curl http://cd2ia-thomas.stagiairesmns.fr/api/faq

# Test Frontend
curl http://cd2ia-thomas.stagiairesmns.fr/

# Test avec headers
curl -H "Host: cd2ia-thomas.stagiairesmns.fr" http://127.0.0.1/api/faq
```
