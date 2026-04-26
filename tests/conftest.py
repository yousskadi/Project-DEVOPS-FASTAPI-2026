"""
conftest.py — Configuration globale des tests pytest

Ce fichier est automatiquement chargé par pytest avant tous les tests.
Il contient les fixtures partagées entre tous les fichiers de test.

─── Scopes utilisés ────────────────────────────────────────────────────────────
Toutes les fixtures sont en scope="function" (une instance par test).

Pourquoi pas "module" ou "session" ?

  La règle fondamentale des scopes pytest :
    function < class < module < package < session   (du plus étroit au plus large)
  Un fixture ne peut PAS avoir un scope PLUS LARGE que ses dépendances.

  Exemple interdit : si `session` est "function", alors `client` (qui dépend de
  `session`) NE PEUT PAS être "module" — pytest lèverait une erreur.

  Règle pratique : dès que la fixture racine (`session` DB) est "function",
  TOUTE la chaîne de dépendances est forcée à "function".

  Pourquoi `session` DB doit être "function" :
    - Elle fait drop_all + create_all → reset complet des tables
    - Si "module" : test_delete_own_post détruirait le post pour tous les tests
      suivants du module → test_get_post_by_id recevrait 404 par contamination
    - L'isolation parfaite vaut le coût (quelques ms par test)

  Quand élargir les scopes ? Seulement si la suite devient très grande (500+
  tests) et que le setup DB devient un goulot. On adopterait alors le pattern
  "transaction rollback" (scope="session" sur le moteur + rollback dans chaque
  test). Pour ~30 tests, c'est inutile.

Fixtures disponibles :
- session          : session DB de test isolée (tables recréées à chaque test)
- client           : TestClient FastAPI connecté à la DB de test
- token            : JWT token valide pour un utilisateur de test
- authorized_client: client avec le header Authorization déjà configuré
- test_post        : post en DB appartenant à l'utilisateur de test
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


# scope="function" — reset complet (drop_all + create_all) avant chaque test.
# Garantit qu'aucune donnée ne fuite d'un test à l'autre.
# Fixture racine : toute la chaîne de dépendances hérite de ce scope.
@pytest.fixture(scope="function")
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# scope="function" — obligatoire car dépend de `session` (function).
# Réinitialise aussi dependency_overrides après chaque test.
@pytest.fixture(scope="function")
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


# scope="function" — obligatoire car dépend de `session` (function).
# L'id utilisateur change à chaque reset DB (auto-increment repart de 1) ;
# un token "module" pointerait vers un user_id inexistant après le reset.
# Retourne l'objet User pour que `token` et `test_post` partagent la même
# instance sans avoir à refaire une requête DB chacun.
@pytest.fixture(scope="function")
def test_user(session):
    from app.utils import hash_password
    from app.models import User

    user = User(email="test@test.com", password=hash_password("password123"))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# scope="function" — obligatoire car dépend de `test_user` (function).
@pytest.fixture(scope="function")
def token(test_user):
    return oauth2.create_access_token(data={"user_id": test_user.id})


# scope="function" — obligatoire car dépend de `client` et `token` (tous deux function).
@pytest.fixture(scope="function")
def authorized_client(client, token):
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


# scope="function" — obligatoire car dépend de `session` et `test_user` (function).
# Certains tests suppriment ce post (test_delete_own_post) : un scope plus large
# le ferait disparaître pour les tests suivants du même module.
@pytest.fixture(scope="function")
def test_post(session, test_user):
    from app.models import Post

    post = Post(title="Test Post", content="Test content", user_id=test_user.id)
    session.add(post)
    session.commit()
    session.refresh(post)
    return post
