from uuid import UUID
from fastapi.testclient import TestClient
from fastapi import Header

from src.server.main import app
from src.server.models import Token
from src.server.dependencies import token_auth

# This is how to override a dependency


def token_auth_override(token: UUID = Header()) -> Token:
    return "valid"


client = TestClient(app)

app.dependency_overrides[token_auth] = token_auth_override


def test_token_auth() -> None:
    test_token = "f657d7a2-0e80-5cb3-affa-ed2ac5b644da"
    response = client.get(
        "/", headers={"content-type": "application/json", "token": test_token}
    )

    assert response.status_code == 200
    assert response.json()["token"] == "valid"
