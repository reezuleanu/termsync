from fastapi.testclient import TestClient
from mongomock import MongoClient

from src.server.main import app
from src.server.models import User
from src.server.dependencies import db_depend, token_auth, admin_auth
from src.server.database import Database


# mock database class
class MockDatabase(Database):
    def __init__(self) -> None:
        super().__init__()
        self.client = MongoClient()
        self.db = self.client.tests


# mock database instance
db = MockDatabase()


# mock dependency
def db_depend_override() -> MockDatabase:
    """Returns mock database instance"""

    return db


client = TestClient(app)

# mock user data for testing
mock_user = User(username="randomuser", full_name="full name jr.")
mock_password = "password"

# second mock user for tests that require 2 accounts
other_user = User(username="otheruser", full_name="another test user")


def test_setup() -> None:
    """Reset fastapi dependencies then override the ones used in this test"""

    app.dependency_overrides = {}

    # override database with a mock
    app.dependency_overrides[db_depend] = db_depend_override


def test_post_user() -> None:
    """Test creating a user"""

    # create user
    response = client.post(
        "/users/",
        json={
            "user": mock_user.model_dump(),
            "password": mock_password,
        },
    )

    assert response.status_code == 200
    global token  # make token global for further use
    token = response.json()["token"]
    assert token

    # check if user is actually in the database
    response = client.get(
        "/users/randomuser",
        headers={"content-type": "application/json", "token-uuid": token},
    )
    assert response.status_code == 200
    assert response.json()["username"] == mock_user.username


def test_post_user_taken_username() -> None:
    """Test creating a user with an unavailable username"""

    response = client.post(
        "/users/",
        json={
            "user": mock_user.model_dump(),
            "password": mock_password,
        },
    )

    assert response.status_code == 406
    assert response.json()["detail"] == "Username already taken"


def test_login() -> None:
    """Test logging in"""

    response = client.post(
        "/login/", json={"username": mock_user.username, "password": mock_password}
    )

    assert response.status_code == 200
    global token
    token = response.json()["token"]
    assert token


def test_failed_login() -> None:
    """Test trying to log in with a non existing user/bad password"""

    # try logging in with a bad password
    response = client.post(
        "/login/", json={"username": mock_user.username, "password": "bad_password"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

    # try loggin in with a non existing user

    response = client.post(
        "/login/", json={"username": "baduser", "password": "bad_password"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


def test_get_user() -> None:
    """Test getting user data"""

    response = client.get(
        f"/users/{mock_user.username}",
        headers={"content-type": "application/json", "token-uuid": token},
    )

    assert response.status_code == 200
    assert response.json()["username"] == mock_user.username


def test_get_missing_user() -> None:
    """Test getting data of non existing user"""

    response = client.get(
        "/users/baduser",
        headers={"content-type": "application/json", "token-uuid": token},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_modify_user() -> None:
    """Test modifying the user"""

    global mock_user
    mock_user = User(username="randomuser", full_name="full name senior")

    response = client.put(
        f"/users/{mock_user.username}",
        headers={"content-type": "application/json", "token-uuid": token},
        json=mock_user.model_dump(),
    )

    assert response.status_code == 200
    assert response.json()["detail"] == "User updated successfully"

    response = client.get(
        f"/users/{mock_user.username}",
        headers={"content-type": "application/json", "token-uuid": token},
    )

    # check the full name actually changed
    assert response.status_code == 200
    assert response.json()["full_name"] == mock_user.full_name


def test_modify_other_user() -> None:
    """Test modifying another user as a non admin"""

    # add second user for testing
    response = client.post(
        "/users/", json={"user": other_user.model_dump(), "password": mock_password}
    )

    # make sure the user was added
    assert response.status_code == 200
    global other_token
    other_token = response.json()["token"]

    modified_user = User(
        username=other_user.username, full_name="modified test full name"
    )

    response = client.put(
        f"/users/{other_user.username}",
        headers={"content-type": "application/json", "token-uuid": token},
        json=modified_user.model_dump(),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "You cannot modify another user's account"


def test_modify_username() -> None:
    """Test changing username"""

    modified_user = User(**mock_user.model_dump())
    modified_user.username = "modifiedusername"

    response = client.put(
        f"/users/{mock_user.username}",
        headers={"content-type": "application/json", "token-uuid": token},
        json=modified_user.model_dump(),
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "You cannot change the username"

    # check the username in the database didn't change
    response = client.get(
        f"/users/{mock_user.username}",
        headers={"content-type": "application/json", "token-uuid": token},
    )

    assert (
        response.json()["username"] == mock_user.username
        and response.json()["username"] != modified_user.username
    )


def test_deleting_other_user() -> None:
    """Test deleting another user as a non admin"""

    # apparently starlette removed payloads from delete requests
    # response = client.delete(
    #     f"/users/{other_user.username}",
    #     headers={"content-type": "application/json", "token-uuid": token},
    #     json={"password": mock_password},
    # )

    # workaround
    response = client.request(
        "DELETE",
        f"/users/{other_user.username}",
        headers={"content-type": "application/json", "token-uuid": token},
        json=mock_password,
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "You cannot delete someone else's account"


def test_deleting_bad_user() -> None:
    "Test deleting non existing user/with bad password"

    # non existing user
    response = client.request(
        "DELETE",
        "/users/nonexistinguser",
        headers={"content-type": "application/json", "token-uuid": token},
        json=mock_password,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Could not find user"

    # bad password
    response = client.request(
        "DELETE",
        f"/users/{mock_user.username}",
        headers={"content-type": "application/json", "token-uuid": token},
        json="bad password",
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect password"


def test_make_admin() -> None:
    """Test making a user an admin (must be an admin yourself)"""

    # make self admin
    db.db.users.update_one(
        {"username": mock_user.username}, {"$set": {"power": "admin"}}
    )

    # make other user admin
    response = client.post(
        f"/admin/{other_user.username}",
        headers={"content-type": "application/json", "token-uuid": token},
    )

    assert response.status_code == 200
    assert response.json()["detail"] == "User promoted to admin successfully"

    # double check user is now admin
    response = client.get(
        "/", headers={"content-type": "application/json", "token-uuid": other_token}
    )

    assert response.json()["admin"] is True


def test_delete_user() -> None:
    """Test deleting user"""

    response = client.request(
        "DELETE",
        f"/users/{mock_user.username}",
        headers={"content-type": "application/json", "token-uuid": token},
        json=mock_password,
    )

    assert response.status_code == 200
    assert response.json()["detail"] == "User deleted successfully"

    # check the user is gone from the database
    response = client.get(
        f"/users/{mock_user.username}",
        headers={"content-type": "application/json", "token-uuid": other_token},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
