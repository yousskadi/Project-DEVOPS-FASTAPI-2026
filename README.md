# FastAPI DevOps Playground - Branche ORM (SQLAlchemy)

Cette branche contient l'application FastAPI modifiée pour utiliser **SQLAlchemy** comme ORM.

---

## ⚙️ Installation des dépendances

1. Assurez-vous d’être sur la branche `feature/fastapi-ORM` :

```bash
git checkout feature/fastapi-ORM
```
2. Créez et activez un venv Linux si ce n’est pas déjà fait :
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Installez les dépendances avec le requirements.txt mis à jour :

```bash
pip install -r requirements.txt

```
4. Launch FastAPI app
```bash
uvicorn app.main:app --reload --port 8080
```


## Query Parameters
What's a query parameters ?
Query parameters are a way to send additional information to the server when making a request. They are appended to the URL and typically follow a `?` character. Each parameter is a key-value pair, and multiple parameters are separated by `&`. For example:
Use Postman to test the API
example for my api : with limit,skip, search ?
    {{URL}}posts?limit=3
    {{URL}}posts?search=Aquida
    {{URL}}posts?search=Aquida&limit=3&skip=2
if search with a space in the URL add %20
  to serach "seminars fiqh"
    {{URL}}posts?search=seminars%20fiqh