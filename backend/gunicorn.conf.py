# Configuration Gunicorn pour FAQ-IA
import multiprocessing

# Serveur
bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 300  # Augmenté à 5 minutes pour la génération IA
keepalive = 2

# Répertoire de travail
chdir = "/var/www/html/faq-IA/backend"

# Logs
accesslog = "/var/log/faq-ia/access.log"
errorlog = "/var/log/faq-ia/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "faq-ia"

# Server mechanics
daemon = False
pidfile = "/var/run/faq-ia/faq-ia.pid"
user = "www-data"
group = "www-data"
tmp_upload_dir = None

# SSL (décommentez si vous utilisez HTTPS)
# keyfile = "/path/to/ssl/keyfile.key"
# certfile = "/path/to/ssl/certfile.crt"
