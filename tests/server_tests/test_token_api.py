from uuid import UUID
from fastapi.testclient import TestClient
from fastapi import Header
from mongomock import MongoClient

from src.server.main import app
from src.server.models import Token, User
from src.server.dependencies import token_auth, admin_auth, db_depend
from src.server.database import Database


# This is how to override a dependency
def token_auth_override() -> User:
    return User(username="randomuser", full_name="random user jr.")


def admin_auth_override() -> bool:
    return False


client = TestClient(app)


def test_setup() -> None:
    """Reset fastapi dependencies then override the ones used in this test"""

    app.dependency_overrides = {}
    app.dependency_overrides[token_auth] = token_auth_override
    app.dependency_overrides[admin_auth] = admin_auth_override


def test_token_auth() -> None:
    """Test token dependency in / endpoint"""
    test_token = "test_token"
    response = client.get(
        "/", headers={"content-type": "application/json", "token-uuid": test_token}
    )

    assert response.status_code == 200
    assert response.json()["response"] == "hello there randomuser!"
    assert response.json()["admin"] is False
