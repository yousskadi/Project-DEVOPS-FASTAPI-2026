# Gunicorn - Serveur HTTP Python pour la production

## 📝 C'est quoi Gunicorn ?

**Gunicorn** (Green Unicorn) est un serveur HTTP WSGI pour Python. C'est le standard pour déployer des applications Python en production. Il agit comme un **gestionnaire de processus** qui crée et supervise plusieurs workers pour traiter les requêtes entrantes.

---

## 🏗️ Architecture

```
Client
  │
  ▼
Nginx (reverse proxy)
  │
  ▼
Gunicorn (master process)
  ├── Worker 1 ──► FastAPI app
  ├── Worker 2 ──► FastAPI app
  ├── Worker 3 ──► FastAPI app
  └── Worker 4 ──► FastAPI app
```

- Le **master process** gère les workers (démarrage, arrêt, redémarrage)
- Chaque **worker** traite des requêtes indépendamment
- Si un worker crash, le master en redémarre un automatiquement

---

## ❓ Pourquoi pas Uvicorn seul ?

| | Uvicorn seul | Gunicorn + Uvicorn |
|---|---|---|
| Workers | 1 processus | Plusieurs processus |
| Cores CPU | 1 seul core | Tous les cores |
| Crash recovery | ❌ | ✅ |
| Reload auto | ✅ (dev only) | ❌ |
| Production ready | ❌ | ✅ |

---

## ⚙️ Installation

```bash
pip install gunicorn
```

---

## 🚀 Commande de base

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8080
```

### Détail des options

| Option | Valeur | Description |
|---|---|---|
| `-w` | `4` | Nombre de workers |
| `-k` | `uvicorn.workers.UvicornWorker` | Type de worker (obligatoire pour FastAPI) |
| `app.main:app` | - | Chemin vers l'instance FastAPI |
| `--bind` | `0.0.0.0:8080` | Interface et port d'écoute |

---

## 📋 Options et features

### Nombre de workers
```bash
# Règle recommandée : (2 x CPU cores) + 1
gunicorn -w 4 ...         # 4 workers (machine 2 cores)
gunicorn -w 9 ...         # 9 workers (machine 4 cores)
```

### Timeout
```bash
# Temps max (en secondes) avant de killer un worker bloqué (défaut: 30s)
gunicorn --timeout 60 ...
```

### Logs
```bash
# Niveau de log
gunicorn --log-level debug ...
gunicorn --log-level info ...
gunicorn --log-level warning ...

# Fichiers de log
gunicorn --access-logfile logs/access.log --error-logfile logs/error.log ...
```

### Graceful reload (sans downtime)
```bash
# Recharger les workers sans couper le service
kill -HUP <master_pid>

# Ou avec la commande
gunicorn --reload ...   # ⚠️ dev uniquement
```

### Daemon mode (arrière-plan)
```bash
gunicorn --daemon ...
```

### Fichier de configuration
```bash
gunicorn -c gunicorn.conf.py app.main:app
```

---

## 📁 Fichier de configuration `gunicorn.conf.py`

Plutôt que de tout passer en ligne de commande, créer un fichier de config :

```python
# gunicorn.conf.py

bind = "0.0.0.0:8080"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 60
keepalive = 5
log_level = "info"
accesslog = "logs/access.log"
errorlog = "logs/error.log"
```

Puis lancer avec :
```bash
gunicorn -c gunicorn.conf.py app.main:app
```

---

## 🔄 Types de workers

| Worker | Usage |
|---|---|
| `sync` | Défaut, applications synchrones (Flask, Django) |
| `uvicorn.workers.UvicornWorker` | Applications async (FastAPI, Starlette) |
| `gevent` | Applications I/O intensives |
| `gthread` | Multi-threading |

> Pour **FastAPI**, toujours utiliser `uvicorn.workers.UvicornWorker`

---

## 🌍 Dev vs Production

```bash
# Développement
uvicorn app.main:app --reload --port 8080

# Production
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8080
```

> ⚠️ Ne jamais utiliser `--reload` en production

---

## 🔒 Avec Nginx (recommandé en production)

Nginx reçoit les requêtes et les transmet à Gunicorn via un socket Unix (plus performant que TCP) :

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📦 Avec Systemd (service Linux)

Pour lancer Gunicorn automatiquement au démarrage du serveur :

```ini
# /etc/systemd/system/fastapi.service

[Unit]
Description=FastAPI app
After=network.target

[Service]
User=www-data
WorkingDirectory=/home/youssef/Project-DEVOPS-FASTAPI-2026
ExecStart=/home/youssef/Project-DEVOPS-FASTAPI-2026/venv/bin/gunicorn \
          -w 4 \
          -k uvicorn.workers.UvicornWorker \
          app.main:app \
          --bind 0.0.0.0:8080
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Activer et démarrer le service
sudo systemctl enable fastapi
sudo systemctl start fastapi
sudo systemctl status fastapi
```

---

## 🔗 Ressources

- [Documentation officielle Gunicorn](https://docs.gunicorn.org/en/stable/)
- [Uvicorn + Gunicorn](https://www.uvicorn.org/deployment/#gunicorn)
