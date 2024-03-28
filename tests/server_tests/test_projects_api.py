from fastapi.testclient import TestClient
from mongomock import MongoClient

from src.server.main import app
from src.server.models import User, Project
from src.server.dependencies import db_depend
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


# init client
client = TestClient(app)

# mock users
user1 = User(username="mockuser1", full_name="fullname1")  # project owner
user2 = User(username="mockuser2", full_name="fullname2")  # project moderator
user3 = User(username="mockuser3", full_name="fullname3")  # project member
admin_user = User(username="adminuser", full_name="admin user")  # admin user

# mock project
mockproject = Project(name="mock project", description="this is a mock project")


def test_setup() -> None:
    """Reset fastapi dependencies then override the ones used in this test and create mock users"""

    app.dependency_overrides = {}
    # override database with a mock
    app.dependency_overrides[db_depend] = db_depend_override

    # create mock users
    global token1
    token1 = client.post(
        "/users/", json={"user": user1.model_dump(), "password": "password"}
    ).json()["token"]

    global token2
    token2 = client.post(
        "/users/", json={"user": user2.model_dump(), "password": "password"}
    ).json()["token"]

    global token3
    token3 = client.post(
        "/users/", json={"user": user3.model_dump(), "password": "password"}
    ).json()["token"]

    global admin_token
    admin_token = client.post(
        "/users/", json={"user": admin_user.model_dump(), "password": "password"}
    ).json()["token"]

    # make admin_user an admin
    db.db.users.update_one(
        {"username": admin_user.username}, {"$set": {"power": "admin"}}
    )


# POST TESTS
def test_create_project() -> None:
    """Successfully create a project"""

    response = client.post(
        "/projects/",
        headers={"content-type": "application/json", "token-uuid": token1},
        json=mockproject.model_dump(),
    )
    assert response.status_code == 200
    assert response.json()["detail"] == "Project created successfully"


def test_create_project_taken_name() -> None:
    """Try to create a project when the name is already taken"""

    response = client.post(
        "/projects/",
        headers={"content-type": "application/json", "token-uuid": token1},
        json=mockproject.model_dump(),
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Project already exists"


# GET TESTS
def test_get_project() -> None:
    """Get project data"""

    response = client.get(
        f"/projects/{mockproject.name}",
        headers={"content-type": "application/json", "token-uuid": token1},
    )

    assert response.status_code == 200
    # verify attributes match
    assert response.json()["name"] == mockproject.name
    assert response.json()["description"] == mockproject.description
    assert response.json()["owner"] == user1.username


def test_get_nonexisting_project() -> None:
    """Try to get data of a non existing project"""

    response = client.get(
        "/projects/nonexistingproject",
        headers={"content-type": "application/json", "token-uuid": token1},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


def test_get_project_not_member() -> None:
    """Try to get data of a project you are not a member of"""

    response = client.get(
        f"/projects/{mockproject.name}",
        headers={"content-type": "application/json", "token-uuid": token2},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "You are not a member of this project"


def test_get_project_admin() -> None:
    """Get data of a project you are not a member of, as an admin"""

    response = client.get(
        f"/projects/{mockproject.name}",
        headers={"content-type": "application/json", "token-uuid": admin_token},
    )

    assert response.status_code == 200
    assert response.json()["name"] == mockproject.name


# UPDATE TESTS
def test_update_project() -> None:
    """Update project data as owner (currently that is only the description)"""

    # get latest project data
    project = Project(
        **client.get(
            f"/projects/{mockproject.name}",
            headers={"content-type": "application/json", "token-uuid": token1},
        ).json()
    )

    # modify the description then send it to the API
    project.description = "Updated description"
    response = client.put(
        f"/projects/{mockproject.name}",
        headers={"content-type": "application/json", "token-uuid": token1},
        json=project.model_dump(),
    )

    assert response.status_code == 200

    # get latest project data from API for double checking
    response = client.get(
        f"/projects/{mockproject.name}",
        headers={"content-type": "application/json", "token-uuid": token1},
    )

    assert response.status_code == 200
    updated_project = Project(**response.json())
    assert updated_project.name == project.name
    assert updated_project.description == project.description
    assert updated_project.owner == user1.username

    # update global test project data
    mockproject.description = updated_project.description


def test_update_name() -> None:
    """Try to modify project name"""

    # get latest project data
    project = Project(
        **client.get(
            f"/projects/{mockproject.name}",
            headers={"content-type": "application/json", "token-uuid": token1},
        ).json()
    )

    # modify name and send it to the API
    project.name = "Updated name"
    response = client.put(
        f"/projects/{mockproject.name}",
        headers={"content-type": "application/json", "token-uuid": token1},
        json=project.model_dump(),
    )

    # assert failure
    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot modify project name"


# PROJECT MEMBERS TESTS
def test_add_member() -> None:
    """Add a user to the project"""

    response = client.post(
        f"/projects/{mockproject.name}/members/{user2.username}",
        headers={"content-type": "application/json", "token-uuid": token1},
    )

    # assert API response
    assert response.status_code == 200
    assert response.json()["detail"] == "User added to project successfully"

    # assert member in project
    project = Project(
        **client.get(
            f"/projects/{mockproject.name}",
            headers={"content-type": "application/json", "token-uuid": token1},
        ).json()
    )

    assert user2.username in project.members


def test_add_duplicate_member() -> None:
    """Try to add a user that is already part of the project"""

    response = client.post(
        f"/projects/{mockproject.name}/members/{user2.username}",
        headers={"content-type": "application/json", "token-uuid": token1},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "User already part of project"


def test_add_nonexisting_member() -> None:
    """Try to add a user that does not exist"""

    response = client.post(
        f"/projects/{mockproject.name}/members/randomuserthatdoesnotexist",
        headers={"content-type": "application/json", "token-uuid": token1},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User does not exist"


def test_unauthorized_add_member() -> None:
    """Try to add a use to the project when you don't have permission to do so"""

    response = client.post(
        f"/projects/{mockproject.name}/members/{user3.username}",
        headers={"content-type": "application/json", "token-uuid": token2},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You cannot add members to this project"


def test_add_member_admin() -> None:
    """Add a member to a project you are not part of as an admin"""

    response = client.post(
        f"/projects/{mockproject.name}/members/{user3.username}",
        headers={"content-type": "application/json", "token-uuid": admin_token},
    )

    assert response.status_code == 200
    assert response.json()["detail"] == "User added to project successfully"

    project = Project(
        **client.get(
            f"/projects/{mockproject.name}",
            headers={"content-type": "application/json", "token-uuid": token1},
        ).json()
    )

    assert user3.username in project.members


def test_remove_member_not_authorized() -> None:
    """Remove member without having enough permissions"""

    response = client.delete(
        f"/projects/{mockproject.name}/members/{user3.username}",
        headers={"content-type": "application/json", "token-uuid": token2},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You cannot remove members from this project"


def test_remove_non_existing_member() -> None:
    """Remove a member that does not exist"""

    response = client.delete(
        f"/projects/{mockproject.name}/members/nonexistinguser",
        headers={"content-type": "application/json", "token-uuid": token1},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User is not part of the project"


def test_remove_member() -> None:
    """Remove a member from project"""

    response = client.delete(
        f"/projects/{mockproject.name}/members/{user2.username}",
        headers={"content-type": "application/json", "token-uuid": token1},
    )

    assert response.status_code == 200
    assert response.json()["detail"] == "User removed from project successfully"


def test_remove_member_admin() -> None:
    """Remove a member from the project as admin"""

    # add user 2 back to project
    response = client.post(
        f"/projects/{mockproject.name}/members/{user2.username}",
        headers={"content-type": "application/json", "token-uuid": admin_token},
    )

    assert response.status_code == 200

    # delete member as admin, not owner or moderator
    response = client.delete(
        f"/projects/{mockproject.name}/members/{user2.username}",
        headers={"content-type": "application/json", "token-uuid": admin_token},
    )

    assert response.status_code == 200
    assert response.json()["detail"] == "User removed from project successfully"


def test_make_moderator() -> None:
    """Add user to project and make them a moderator"""

    # add user
    response = client.post(
        f"/projects/{mockproject.name}/members/{user2.username}",
        headers={"content-type": "application/json", "token-uuid": token1},
    )

    assert response.status_code == 200

    # make moderator
    response = client.post(
        f"/projects/{mockproject.name}/moderators/{user2.username}",
        headers={"content-type": "application/json", "token-uuid": token1},
    )

    assert response.status_code == 200
    assert response.json()["detail"] == "Moderator added successfully"

    # get latest data from API and check if user is a moderator
    project = Project(
        **client.get(
            f"/projects/{mockproject.name}",
            headers={"content-type": "application/json", "token-uuid": token1},
        ).json()
    )

    assert user2.username in project.moderators


def test_remove_moderator() -> None:
    """Demote user from being a moderator"""

    response = client.delete(
        f"/projects/{mockproject.name}/moderators/{user2.username}",
        headers={"content-type": "application/json", "token-uuid": token1},
    )

    assert response.status_code == 200
    assert response.json()["detail"] == "User demoted successfully"
