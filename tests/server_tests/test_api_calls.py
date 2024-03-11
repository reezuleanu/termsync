# global imports
import requests
from uuid import UUID

# relative imports
from src.server.models import User, Token, Project, Task

# app url and port, change if needed
api = "http://127.0.0.1:2727"

# mock user object to be used for tests
user = User(username="randomuser", full_name="pulea spataru")
password = "123"

# mock task objects
task1 = None
task2 = None
task3 = None

# mock project
project = None


def test_token():
    response = requests.get(
        f"{api}/",
        headers={
            "content-type": "application/json",
            "token-uuid": "12761244-6134-5a0e-9939-d8284e50be2f",
        },
    )

    assert response.status_code == 200


def test_post_user():
    """Call which should return an User object"""
    response = requests.post(
        f"{api}/user/", json={"user": user.model_dump(), "password": password}
    )
    assert response.status_code == 200
    global other_user  # will use this when trying to delete it
    other_user = User(**response.json())
    assert other_user.username == user.username
    assert other_user.full_name == user.full_name
    assert other_user.id != None


def test_post_taken_username():
    """Call which attempts to create a user with a taken username"""
    response = requests.post(
        f"{api}/user/", json={"user": user.model_dump(), "password": password}
    )
    assert response.status_code == 406
    assert response.json()["detail"] == "username already taken"


def test_login_user():
    """Call which logs in using the newly created user"""
    response = requests.get(
        f"{api}/login/", json={"username": user.username, "password": password}
    )
    assert response.status_code == 200
    global token

    # token validation
    token = Token(**response.json())
    assert token


def test_hello():
    """Test of simple hello call"""
    response = requests.get(
        api, headers={"content-type": "applicaton/json", "token": str(token.token)}
    )
    assert response.status_code == 200
    assert response.json()["response"] == "hello there!"


def test_invalid_token():
    """Test of hello call, with an invalid token. Should fail"""
    response = requests.get(
        api,
        headers={
            "content-type": "application/json",
            "token": "99999999-9999-9999-9999-20692ac2eafb",  # bad token
        },
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Unauthorized access"


def test_get_user():
    """Call which tries to get user data from the database"""

    response = requests.get(f"{api}/user/", params={"username": user.username})
    assert response.status_code == 200
    assert User(**response.json()).username == user.username


def test_get_nonexisting_user():
    """Call which attempts to get data from a non existing user"""

    response = requests.get(f"{api}/user/", params={"username": "nonexistingusername"})
    assert response.status_code == 404
    assert response.json()["detail"] == "could not find user"


def test_update_user():
    """Call which update user data in the database"""
    global user
    modified_user = other_user.model_dump()
    modified_user["full_name"] = "dan diaconescu"
    modified_user = User(**modified_user)

    response = requests.put(f"{api}/user/", json=modified_user.model_dump())

    assert response.status_code == 200
    user = User(**response.json())
    assert User(**response.json()).full_name == modified_user.full_name


def test_update_username():
    """Call which attempts to change the username. Should fail"""

    global user
    modified_user = other_user.model_dump()
    modified_user["username"] = "badusername"
    modified_user = User(**modified_user)

    response = requests.put(f"{api}/user/", json=modified_user.model_dump())

    assert response.status_code == 406
    assert response.json()["detail"] == "you cannot change your username"


def test_delete_unexisting_user():
    """Test that attempts to delete a user that doesn't exist/with an invalid id"""
    response = requests.delete(
        f"{api}/user/",
        json={"id": "badid", "password": "doesn't matter"},
    )

    assert response.status_code == 404 or response.status_code == 406
    assert (
        response.json()["detail"] == "could not find user"
        or response.json()["detail"] == "invalid id"
    )


def test_delete_user_wrong_password():
    """Test that attempts to delete an existing user using the wrong password"""
    response = requests.delete(
        f"{api}/user/",
        json={"id": other_user.id, "password": "wrong password"},
    )
    assert response.status_code == 406
    assert response.json()["detail"] == "incorrect password"


def test_post_project():
    """Test that adds a project to the database"""

    global project
    project = Project(
        owner_id=other_user.id,
        name="im going insane132",
        description="this is a test project",
    )

    response = requests.post(
        f"{api}/projects/",
        headers={"content-type": "application/json", "token": str(token.token)},
        json={"project": project.model_dump()},
    )

    assert response.status_code == 200
    returned_project = Project(**response.json())
    assert returned_project
    assert returned_project.name == project.name
    assert returned_project.description == project.description
    assert returned_project.owner_id == other_user.id

    project = returned_project


def test_update_project():

    task1 = Task(name="add a task")
    task2 = Task(name="add a task with a member", members=[other_user])

    project.add_task(task1)
    project.add_task(task2)
    project.add_member(other_user)

    response = requests.put(
        f"{api}/projects/",
        headers={"content-type": "application/json", "token": str(token.token)},
        json={"project": project.model_dump()},
    )

    assert response.status_code == 200
    other_project = Project(**response.json())
    assert other_project
    assert other_project.name == project.name


def test_delete_project():
    response = requests.delete(
        f"{api}/projects/",
        headers={"content-type": "application/json", "token": str(token.token)},
        json={"id": project.id},
    )

    assert response.status_code == 200
    assert response.json()["detail"] == "project deleted successfully"


def test_delete_user_successful():
    """Call which requests API to delete user from DB"""

    response = requests.delete(
        f"{api}/user/", json={"id": other_user.id, "password": password}
    )
    assert response.status_code == 200
    assert response.json()["detail"] == "user deleted successfully"
