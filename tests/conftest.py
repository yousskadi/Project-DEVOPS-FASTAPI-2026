"""
conftest.py — Configuration globale des tests pytest

Ce fichier est automatiquement chargé par pytest avant tous les tests.
Il contient les fixtures partagées entre tous les fichiers de test.

Fixtures disponibles :
- session         : session DB de test isolée (tables recréées à chaque test)
- client          : TestClient FastAPI connecté à la DB de test
- token           : JWT token valide pour un utilisateur de test
- authorized_client : client avec le header Authorization déjà configuré
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app import oauth2
from app.config import settings

# ---------------------------------------------------------------
# Base de données de test (séparée de la DB de production)
# Utilise les mêmes credentials mais avec le suffixe _test
# Ex: fastapi_db → fastapi_db_test
# ---------------------------------------------------------------
SQLALCHEMY_TEST_DATABASE_URL = (
    f"postgresql+psycopg://{settings.DB_USERNAME}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOSTNAME}:{settings.DB_PORT}/{settings.DB_NAME}_test"
)

def create_test_database():
    """
    Crée la base de données de test si elle n'existe pas.
    Se connecte à la DB 'postgres' (DB système toujours disponible) pour exécuter
    le CREATE DATABASE, car PostgreSQL interdit de créer une DB depuis elle-même.
    On dérive l'URL depuis SQLALCHEMY_TEST_DATABASE_URL en remplaçant juste le nom de la DB.
    """
    # Remplace le nom de la DB de test par 'postgres' pour la connexion initiale
    bootstrap_url = SQLALCHEMY_TEST_DATABASE_URL.rsplit("/", 1)[0] + "/postgres"
    default_engine = create_engine(bootstrap_url, isolation_level="AUTOCOMMIT")
    with default_engine.connect() as conn:
        db_name = f"{settings.DB_NAME}_test"
        exists = conn.execute(
            text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        ).fetchone()
        if not exists:
            conn.execute(text(f"CREATE DATABASE {db_name}"))
            print(f"✅ Base de données '{db_name}' créée automatiquement")
    default_engine.dispose()

create_test_database()

engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def session():
    """
    Fixture DB : fournit une session SQLAlchemy connectée à la DB de test.

    Avant chaque test :
      - drop_all  → supprime toutes les tables (données du test précédent)
      - create_all → recrée les tables vides (état propre garanti)

    Après chaque test :
      - ferme la connexion DB
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    """
    Fixture client HTTP : fournit un TestClient FastAPI utilisant la DB de test.

    Override la dépendance get_db de FastAPI pour injecter la session de test
    à la place de la session de production. Cela garantit que les requêtes
    HTTP des tests n'affectent jamais la DB de production.
    """
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    # Nettoyage : restaure les dépendances originales après le test
    app.dependency_overrides.clear()


@pytest.fixture()
def token(session):
    """
    Fixture token : crée un utilisateur de test en DB et retourne un JWT valide.

    On insère l'utilisateur directement en DB (sans passer par POST /users/)
    car cet endpoint est protégé et nécessite lui-même un token.
    """
    from app.utils import hash_password
    from app.models import User

    user = User(email="test@test.com", password=hash_password("password123"))
    session.add(user)
    session.commit()
    session.refresh(user)
    return oauth2.create_access_token(data={"user_id": user.id})


@pytest.fixture()
def authorized_client(client, token):
    """
    Fixture client authentifié : client HTTP avec le header Authorization configuré.

    Combine les fixtures client + token pour simuler un utilisateur connecté.
    À utiliser pour tous les endpoints protégés par JWT.
    """
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client
