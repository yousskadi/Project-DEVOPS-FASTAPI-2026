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