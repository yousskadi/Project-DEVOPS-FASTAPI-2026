<<<<<<< HEAD
# FastAPI DevOps Playground

Ce projet est un **playground DevOps** autour d'une application FastAPI avec PostgreSQL.
L'objectif est de créer une application API REST fonctionnelle, puis de mettre en place **tout le cycle CI/CD et DevOps**.

---

## 🏗️ Étape 1 : Création de l'API FastAPI

Cette étape contient :

- Une API FastAPI minimale avec un endpoint `/health` et gestion des posts.
- Connexion à une base PostgreSQL via `psycopg3`.
- Endpoints CRUD pour `posts`.

### 📁 Structure du projet

Fastapi/
├── app/
│ ├── main.py # Entrée de l'application FastAPI
│ ├── routers/ # Endpoints (à venir)
│ ├── schemas/ # Modèles Pydantic
│ ├── database.py # Connexion à PostgreSQL
│ └── init.py
├── tests/ # Tests unitaires / API
├── requirements.txt
├── .env.example # Exemple de variables d'environnement
└── README.md


---

## ⚙️ Installation & Pré-requis

1. Assurez-vous d’avoir **Python 3.11+** et **PostgreSQL** installés sur votre machine WSL/Linux.
2. Créez un environnement virtuel :

=======
# FastAPI DevOps Playground - Social Media API

## 📝 Description

API REST complète construite avec **FastAPI** et **SQLAlchemy ORM** pour gérer un système de posts de type réseau social. L'application inclut l'authentification JWT, la gestion des utilisateurs, les posts et un système de votes.

## ✨ Fonctionnalités

- 🔐 **Authentification JWT** avec tokens expirables
- 👤 **Gestion des utilisateurs** (inscription, connexion)
- 📄 **CRUD complet pour les posts** (Create, Read, Update, Delete)
- 👍 **Système de votes** (like/unlike)
- 🔍 **Recherche et pagination** des posts
- 🔒 **Autorisation** : seul le propriétaire peut modifier/supprimer ses posts
- 🗄️ **Base de données PostgreSQL** avec SQLAlchemy ORM
- 📊 **Validation des données** avec Pydantic V2

## 🏗️ Architecture

```
app/
├── routers/          # Routes API organisées par domaine
│   ├── auth.py       # Authentification (login)
│   ├── post.py       # CRUD posts
│   ├── user.py       # Gestion utilisateurs
│   └── votes.py      # Système de votes
├── models.py         # Modèles SQLAlchemy (Post, User, Votes)
├── schemas.py        # Schémas Pydantic pour validation
├── database.py       # Configuration base de données
├── oauth2.py         # Gestion JWT tokens
├── utils.py          # Utilitaires (hash password)
└── main.py           # Point d'entrée FastAPI
```

## 🗄️ Modèles de données

### Post
- `id`: Identifiant unique
- `title`: Titre du post
- `content`: Contenu
- `published`: Statut de publication
- `created_at`: Date de création
- `user_id`: Référence vers l'utilisateur propriétaire

### User
- `id`: Identifiant unique
- `email`: Email (unique)
- `password`: Mot de passe hashé
- `created_at`: Date de création

### Votes
- `post_id`: Référence vers le post
- `user_id`: Référence vers l'utilisateur

## ⚙️ Installation

### Prérequis
- Python 3.12+
- PostgreSQL

### Étapes d'installation

1. **Cloner le repository et basculer sur la branche ORM**
```bash
git checkout feature/fastapi-ORM
```

2. **Créer et activer l'environnement virtuel**
>>>>>>> feature/add-testing
```bash
python3 -m venv venv
source venv/bin/activate
```

<<<<<<< HEAD
3. Installez les dépendances :
```bash
pip install -r requirements.txt
```
4. Créez un fichier .env à partir de .env.example :
```bash
cp .env.example .env
```
🚀 Lancer l'application
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

- L’API sera accessible sur : http://127.0.0.1:8080

- Documentation interactive Swagger : http://127.0.0.1:8080/docs

- Documentation ReDoc : http://127.0.0.1:8080/redoc

📝 Endpoints disponibles
Méthode	Endpoint	Description

| Méthode | Endpoint      | Description                       |
| ------- | ------------- | --------------------------------- |
| GET     | `/`           | Endpoint de test "Salam Aleykoum" |
| GET     | `/posts`      | Récupérer tous les posts          |
| GET     | `/posts/{id}` | Récupérer un post par id          |
| POST    | `/posts`      | Créer un nouveau post             |
| PUT     | `/posts/{id}` | Mettre à jour un post             |
| DELETE  | `/posts/{id}` | Supprimer un post                 |


🧪 Test rapide

a- Assurez-vous que PostgreSQL est lancé et la base fastapi_db existe.

Lancez l’application :
```bash
    uvicorn app.main:app --reload
```

Testez l’endpoint / dans votre navigateur ou via curl :
```bash
curl http://127.0.0.1:8080/
```
# {"message":"Salam Aleykoum all the World"}
=======
3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer PostgreSQL**

Créer une base de données PostgreSQL :
```sql
CREATE DATABASE fastapi_db;
CREATE USER fastapi WITH PASSWORD 'fastapi';
GRANT ALL PRIVILEGES ON DATABASE fastapi_db TO fastapi;
```

5. **Configurer les variables d'environnement** (optionnel)

Créer un fichier `.env` :
```env
DB_HOSTNAME=localhost
DB_PORT=5432
DB_PASSWORD=fastapi
DB_NAME=fastapi_db
DB_USERNAME=fastapi
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

6. **Lancer l'application**

en local
```bash
uvicorn app.main:app --reload --port 8080
```
en production
```bash
uvicorn --host 0.0.0.0 app.main:app --reload --port 8080
```

6-bis **Utiliser gunicorn
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8080
```

L'API sera accessible sur : `http://localhost:8080`

Documentation interactive : `http://localhost:8080/docs`

## 🚀 Utilisation de l'API

### Authentification

**1. Créer un compte**
```http
POST /users/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**2. Se connecter**
```http
POST /login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=securepassword
```

Réponse :
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**3. Utiliser le token**

Ajouter le header à toutes les requêtes protégées :
```
Authorization: Bearer <votre_token>
```

### Posts

**Créer un post**
```http
POST /posts/
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Mon premier post",
  "content": "Contenu du post",
  "published": true
}
```

**Récupérer tous les posts**
```http
GET /posts/
Authorization: Bearer <token>
```

**Récupérer un post spécifique**
```http
GET /posts/{id}
Authorization: Bearer <token>
```

**Mettre à jour un post**
```http
PUT /posts/{id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Titre modifié",
  "content": "Contenu modifié",
  "published": true
}
```

**Supprimer un post**
```http
DELETE /posts/{id}
Authorization: Bearer <token>
```

### Votes

**Voter pour un post (like)**
```http
POST /votes/
Authorization: Bearer <token>
Content-Type: application/json

{
  "post_id": 1,
  "dir": 1
}
```

**Retirer son vote (unlike)**
```http
POST /votes/
Authorization: Bearer <token>
Content-Type: application/json

{
  "post_id": 1,
  "dir": 0
}
```

## 🔍 Query Parameters

Les query parameters permettent de filtrer et paginer les résultats :

**Pagination**
```
GET /posts?limit=10&skip=0
```
- `limit` : Nombre maximum de résultats (défaut: 10)
- `skip` : Nombre de résultats à ignorer (défaut: 0)

**Recherche**
```
GET /posts?search=FastAPI
```
- `search` : Recherche dans les titres des posts

**Combinaison**
```
GET /posts?search=FastAPI&limit=5&skip=2
```

**Note** : Pour rechercher avec des espaces, utiliser `%20` :
```
GET /posts?search=seminars%20fiqh
```

## 🧪 Tester l'API

### Avec Postman

1. Importer la collection (si disponible)
2. Créer une variable d'environnement `{{URL}}` = `http://localhost:8080`
3. Tester les endpoints

### Avec Swagger UI

Accéder à `http://localhost:8080/docs` pour une interface interactive.

### Peupler la db de données avec Posts,Votes,Users
```bash
 python3 -m example_data.seed_db
```


## 🔒 Sécurité

- Mots de passe hashés avec **bcrypt**
- Authentification par **JWT tokens**
- Tokens expirables (configurable)
- Protection CSRF
- Validation des données avec Pydantic

## 📦 Technologies utilisées

- **FastAPI** : Framework web moderne et rapide
- **SQLAlchemy** : ORM Python
- **PostgreSQL** : Base de données relationnelle
- **Pydantic V2** : Validation des données
- **JWT** : Authentification par tokens
- **Bcrypt** : Hashage des mots de passe
- **Uvicorn** : Serveur ASGI

## 📝 Notes de migration Pydantic V2

Ce projet utilise Pydantic V2. Changements importants :
- `orm_mode = True` → `from_attributes = True`
- `BaseSettings` déplacé vers `pydantic-settings`
- Installation requise : `pip install pydantic-settings`

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

## 📄 Licence

Ce projet est un playground éducatif pour apprendre FastAPI et les pratiques DevOps.
>>>>>>> feature/add-testing
