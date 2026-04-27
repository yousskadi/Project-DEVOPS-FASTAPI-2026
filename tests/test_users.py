"""
test_users.py — Tests des endpoints utilisateurs

Endpoints testés :
- POST /users/       → créer un utilisateur (protégé JWT)
- GET  /users/{id}   → récupérer un utilisateur par id (protégé JWT)

Fixtures utilisées (définies dans conftest.py) :
- authorized_client  → client HTTP avec JWT valide (utilisateur connecté)
- client             → client HTTP sans JWT (utilisateur non connecté)
- session            → session DB pour insérer des données directement
"""

from fastapi import status

# pytest voit "authorized_client"
# cherche dans conftest.py
# injecte automatiquement la fixture
def test_create_user(authorized_client):
    """
    Cas nominal : créer un nouvel utilisateur.
    - Vérifie le status 201 CREATED
    - Vérifie que l'email retourné est correct
    - Vérifie que le mot de passe n'est jamais retourné dans la réponse
    """
    res = authorized_client.post("/users/", json={"email": "newuser@test.com", "password": "password123"})
    print(res.json())
    assert res.status_code == status.HTTP_201_CREATED
    assert res.json()["email"] == "newuser@test.com"
    assert "password" not in res.json()


def test_create_user_duplicate_email(authorized_client):
    """
    Cas d'erreur : créer deux utilisateurs avec le même email.
    - Le 2ème appel doit retourner 400 BAD REQUEST
    """
    authorized_client.post("/users/", json={"email": "duplicate@test.com", "password": "password123"})
    res = authorized_client.post("/users/", json={"email": "duplicate@test.com", "password": "password123"})
    print(res.json())
    assert res.status_code == status.HTTP_400_BAD_REQUEST


def test_get_user_by_id(authorized_client, session):
    """
    Cas nominal : récupérer un utilisateur existant par son id.
    - Insère un utilisateur directement en DB via la session de test
    - Vérifie le status 200 OK
    - Vérifie que l'email retourné correspond bien à l'utilisateur créé
    """
    from app.models import User
    from app.utils import hash_password

    user = User(email="getme@test.com", password=hash_password("password123"))
    session.add(user)
    session.commit()
    session.refresh(user)

    res = authorized_client.get(f"/users/{user.id}")
    print(res.json())
    assert res.status_code == status.HTTP_200_OK
    assert res.json()["email"] == "getme@test.com"


def test_get_user_not_found(authorized_client):
    """
    Cas d'erreur : récupérer un utilisateur avec un id inexistant.
    - Vérifie le status 404 NOT FOUND
    """
    res = authorized_client.get("/users/99999")
    print(res.json())
    assert res.status_code == status.HTTP_404_NOT_FOUND


def test_get_user_unauthorized(client):
    """
    Cas d'erreur : accéder à un endpoint protégé sans token JWT.
    - Utilise le client sans Authorization header
    - Vérifie le status 401 UNAUTHORIZED
    """
    res = client.get("/users/1")
    print(res.json())
    assert res.status_code == status.HTTP_401_UNAUTHORIZED

def test_incorrect_login(authorized_client):
    res = authorized_client.post("/login", data={"username":"fakeemail@gmail.com", "password":"fakepassword"})
    assert res.status_code == status.HTTP_403_FORBIDDEN
    assert res.json().get('detail') == 'Invalid Credentials'
