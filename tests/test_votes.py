"""
test_votes.py — Tests de l'endpoint votes

Endpoint testé :
- POST /votes/  → voter (dir=1) ou retirer son vote (dir=0) sur un post (protégé JWT)

Logique métier :
  dir=1 + vote inexistant  → 201 (vote ajouté)
  dir=1 + vote déjà existant → 409 CONFLICT
  dir=0 + vote existant    → 201 (vote supprimé)
  dir=0 + vote inexistant  → 404
  post inexistant          → 404
  sans token JWT           → 401
  dir invalide (≠ 0 ou 1)  → 422

Fixtures locales :
- test_vote → insère en DB un vote du test_user sur le test_post

Fixtures héritées de conftest.py :
- session, client, token, test_user, authorized_client, test_post
"""

import pytest
from fastapi import status
from app.models import Votes


# ─── Fixture locale ──────────────────────────────────────────────────────────

# scope="function" — obligatoire car dépend de `session`, `test_user`, `test_post`
# (tous function). test_remove_vote supprime ce vote : un scope plus large le
# ferait disparaître avant test_vote_duplicate dans le même module.
@pytest.fixture(scope="function")
def test_vote(session, test_user, test_post):
    """Insère en DB un vote du test_user sur le test_post."""
    vote = Votes(post_id=test_post.id, user_id=test_user.id)
    session.add(vote)
    session.commit()
    return vote


# ─── dir=1 : upvote ──────────────────────────────────────────────────────────

def test_vote_upvote(authorized_client, test_post):
    """Cas nominal : voter sur un post → 201 + message de confirmation."""
    res = authorized_client.post("/votes/", json={"post_id": test_post.id, "dir": 1})
    assert res.status_code == status.HTTP_201_CREATED
    assert res.json() == {"message": "successfully added vote"}


def test_vote_upvote_unauthorized(client, test_post):
    """Cas d'erreur : voter sans token JWT → 401."""
    res = client.post("/votes/", json={"post_id": test_post.id, "dir": 1})
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_vote_on_nonexistent_post(authorized_client):
    """Cas d'erreur : voter sur un post inexistant → 404."""
    res = authorized_client.post("/votes/", json={"post_id": 99999, "dir": 1})
    assert res.status_code == status.HTTP_404_NOT_FOUND


def test_vote_duplicate(authorized_client, test_vote):
    """Cas d'erreur : voter deux fois sur le même post → 409 CONFLICT."""
    res = authorized_client.post("/votes/", json={"post_id": test_vote.post_id, "dir": 1})
    assert res.status_code == status.HTTP_409_CONFLICT


# ─── dir=0 : retrait de vote ─────────────────────────────────────────────────

def test_remove_vote(authorized_client, test_vote):
    """Cas nominal : retirer un vote existant → 201 + message de confirmation."""
    res = authorized_client.post("/votes/", json={"post_id": test_vote.post_id, "dir": 0})
    assert res.status_code == status.HTTP_201_CREATED
    assert res.json() == {"message": "successfully deleted vote"}


def test_remove_vote_nonexistent(authorized_client, test_post):
    """Cas d'erreur : retirer un vote qui n'existe pas → 404."""
    res = authorized_client.post("/votes/", json={"post_id": test_post.id, "dir": 0})
    assert res.status_code == status.HTTP_404_NOT_FOUND


def test_remove_vote_unauthorized(client, test_vote):
    """Cas d'erreur : retirer un vote sans token JWT → 401."""
    res = client.post("/votes/", json={"post_id": test_vote.post_id, "dir": 0})
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


# ─── validation du schéma ────────────────────────────────────────────────────

def test_vote_invalid_dir(authorized_client, test_post):
    """Cas d'erreur : dir=2 interdit par le schéma Literal[0,1] → 422."""
    res = authorized_client.post("/votes/", json={"post_id": test_post.id, "dir": 2})
    assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
