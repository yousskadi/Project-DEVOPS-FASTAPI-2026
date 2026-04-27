"""
test_posts.py — Tests des endpoints posts

Endpoints testés :
- GET    /posts/       → récupérer tous les posts (protégé JWT)
- GET    /posts/{id}   → récupérer un post par id (protégé JWT)
- POST   /posts/       → créer un post (protégé JWT)
- DELETE /posts/{id}   → supprimer un post (protégé JWT, propriétaire uniquement)
- PUT    /posts/{id}   → mettre à jour un post (protégé JWT, propriétaire uniquement)

Fixtures locales :
- second_user_token  → crée un second utilisateur et retourne son JWT
- authorized_client2 → client HTTP authentifié en tant que second utilisateur

Fixtures héritées de conftest.py :
- session, client, token, test_user, authorized_client, test_post
"""

import pytest
from fastapi import status
from app.models import User
from app.utils import hash_password
from app import oauth2


# ─── Fixtures locales ───────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def second_user_token(session):
    """Crée un second utilisateur en DB et retourne son JWT valide."""
    user = User(email="other@test.com", password=hash_password("password456"))
    session.add(user)
    session.commit()
    session.refresh(user)
    return oauth2.create_access_token(data={"user_id": user.id})


@pytest.fixture(scope="function")
def authorized_client2(client, second_user_token):
    """Client HTTP authentifié en tant que second utilisateur (other@test.com)."""
    client.headers.update({"Authorization": f"Bearer {second_user_token}"})
    return client


# ─── GET /posts/ ────────────────────────────────────────────────────────────

def test_get_all_posts(authorized_client, test_post):
    """Cas nominal : récupérer la liste des posts."""
    res = authorized_client.get("/posts/")
    assert res.status_code == status.HTTP_200_OK
    assert isinstance(res.json(), list)
    assert len(res.json()) == 1


def test_get_all_posts_empty(authorized_client):
    """Cas limite : aucun post en DB → liste vide."""
    res = authorized_client.get("/posts/")
    assert res.status_code == status.HTTP_200_OK
    assert res.json() == []


def test_get_all_posts_unauthorized(client):
    """Cas d'erreur : accès sans token JWT → 401."""
    res = client.get("/posts/")
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


# ─── GET /posts/{id} ────────────────────────────────────────────────────────

def test_get_post_by_id(authorized_client, test_post):
    """Cas nominal : récupérer un post existant par son id."""
    res = authorized_client.get(f"/posts/{test_post.id}")
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["Post"]["id"] == test_post.id
    assert data["Post"]["title"] == test_post.title
    assert data["votes"] == 0


def test_get_post_not_found(authorized_client):
    """Cas d'erreur : id inexistant → 404."""
    res = authorized_client.get("/posts/99999")
    assert res.status_code == status.HTTP_404_NOT_FOUND


def test_get_post_by_id_unauthorized(client, test_post):
    """Cas d'erreur : accès sans token JWT → 401."""
    res = client.get(f"/posts/{test_post.id}")
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


# ─── POST /posts/ ───────────────────────────────────────────────────────────

def test_create_post(authorized_client):
    """Cas nominal : créer un post avec tous les champs."""
    payload = {"title": "New Post", "content": "New content", "published": True}
    res = authorized_client.post("/posts/", json=payload)
    assert res.status_code == status.HTTP_201_CREATED
    data = res.json()
    assert data["title"] == "New Post"
    assert data["content"] == "New content"
    assert data["published"] is True


def test_create_post_default_published(authorized_client):
    """Cas limite : published omis → valeur par défaut True."""
    payload = {"title": "No Published Field", "content": "Some content"}
    res = authorized_client.post("/posts/", json=payload)
    assert res.status_code == status.HTTP_201_CREATED
    assert res.json()["published"] is True


def test_create_post_unauthorized(client):
    """Cas d'erreur : création sans token JWT → 401."""
    payload = {"title": "Unauthorized", "content": "Should fail"}
    res = client.post("/posts/", json=payload)
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_post_missing_title(authorized_client):
    """Cas d'erreur : champ title manquant → 422 UNPROCESSABLE ENTITY."""
    res = authorized_client.post("/posts/", json={"content": "No title here"})
    assert res.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_post_missing_content(authorized_client):
    """Cas d'erreur : champ content manquant → 422 UNPROCESSABLE ENTITY."""
    res = authorized_client.post("/posts/", json={"title": "No content here"})
    assert res.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# ─── DELETE /posts/{id} ─────────────────────────────────────────────────────

def test_delete_own_post(authorized_client, test_post):
    """Cas nominal : supprimer son propre post → 204 NO CONTENT."""
    res = authorized_client.delete(f"/posts/{test_post.id}")
    assert res.status_code == status.HTTP_204_NO_CONTENT


def test_delete_post_not_found(authorized_client):
    """Cas d'erreur : supprimer un post inexistant → 404."""
    res = authorized_client.delete("/posts/99999")
    assert res.status_code == status.HTTP_404_NOT_FOUND


def test_delete_post_unauthorized(client, test_post):
    """Cas d'erreur : supprimer sans token JWT → 401."""
    res = client.delete(f"/posts/{test_post.id}")
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_other_user_post(authorized_client2, test_post):
    """Cas d'erreur : supprimer le post d'un autre utilisateur → 403 FORBIDDEN."""
    res = authorized_client2.delete(f"/posts/{test_post.id}")
    assert res.status_code == status.HTTP_403_FORBIDDEN


# ─── PUT /posts/{id} ────────────────────────────────────────────────────────

def test_update_own_post(authorized_client, test_post):
    """Cas nominal : mettre à jour son propre post."""
    payload = {"title": "Updated Title", "content": "Updated content", "published": False}
    res = authorized_client.put(f"/posts/{test_post.id}", json=payload)
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["title"] == "Updated Title"
    assert data["content"] == "Updated content"
    assert data["published"] is False


def test_update_post_not_found(authorized_client):
    """Cas d'erreur : mettre à jour un post inexistant → 404."""
    payload = {"title": "Ghost", "content": "Not here", "published": True}
    res = authorized_client.put("/posts/99999", json=payload)
    assert res.status_code == status.HTTP_404_NOT_FOUND


def test_update_post_unauthorized(client, test_post):
    """Cas d'erreur : mettre à jour sans token JWT → 401."""
    payload = {"title": "Hacked", "content": "No token", "published": True}
    res = client.put(f"/posts/{test_post.id}", json=payload)
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_update_other_user_post(authorized_client2, test_post):
    """Cas d'erreur : mettre à jour le post d'un autre utilisateur → 403 FORBIDDEN."""
    payload = {"title": "Stolen", "content": "Not mine", "published": True}
    res = authorized_client2.put(f"/posts/{test_post.id}", json=payload)
    assert res.status_code == status.HTTP_403_FORBIDDEN
