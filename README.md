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

```bash
python3 -m venv venv
source venv/bin/activate
```

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
