from fastapi.testclient import TestClient
from mongomock import MongoClient

from src.server.main import app
from src.server.models import User, Project, Discrete_Task, Milestone_Task
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
mockproject = Project(
    name="mock project",
    description="this is a mock project",
    members=[user2.username, user3.username],
    moderators=[user2.username],
)


# Mock tasks
mock_discrete_task = Discrete_Task(
    name="Mock Discrete Task", description="This is a mock discrete task for testing"
)

mock_milestone_task = Milestone_Task(
    name="Mock Milestone Task",
    description="This is a mock Milestone task for testing",
    milestones=5,
)

extra_discrete_task = Discrete_Task(
    name="Extra Discrete Task", description="This is an extra discrete task for testing"
)


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

    # add mock project
    client.post(
        "/projects",
        headers={"content-type": "application/json", "token-uuid": token1},
        json=mockproject.model_dump(),
    )

    # check project was setup correctly
    project = Project(
        **client.get(
            f"/projects/{mockproject.name}",
            headers={"content-type": "application/json", "token-uuid": token1},
        ).json()
    )

    assert user1.username == project.owner
    assert user1.username in project.members
    assert user2.username in project.members
    assert user3.username in project.members
    assert user2.username in project.moderators


def test_create_task() -> None:
    """Create tasks as authorized users (owner, moderator and admin).
    Also test creating both types of tasks"""

    # create discrete task as owner
    response = client.post(
        f"/projects/{mockproject.name}/tasks/",
        headers={"content-type": "application/json", "token-uuid": token1},
        json=mock_discrete_task.model_dump(),
    )

    assert response.status_code == 200
    assert response.json()["detail"] == "Task added successfully"

    # create milestone task as moderator
    response = client.post(
        f"/projects/{mockproject.name}/tasks/",
        headers={"content-type": "application/json", "token-uuid": token2},
        json=mock_milestone_task.model_dump(),
    )

    assert response.status_code == 200
    assert response.json()["detail"] == "Task added successfully"

    # create discrete task as admin
    response = client.post(
        f"/projects/{mockproject.name}/tasks/",
        headers={"content-type": "application/json", "token-uuid": admin_token},
        json=extra_discrete_task.model_dump(),
    )

    assert response.status_code == 200
    assert response.json()["detail"] == "Task added successfully"


def test_create_task_unauthorized() -> None:
    """Test creating a task as a mere member"""

    response = client.post(
        f"/projects/{mockproject.name}/tasks/",
        headers={"content-type": "application/json", "token-uuid": token3},
        json=mock_milestone_task.model_dump(),
    )

    assert response.status_code == 403
    assert (
        response.json()["detail"]
        == "You are not authorized to add tasks to this project"
    )


def test_add_task_member() -> None:
    """Test adding members to tasks as project owner, moderator and admin"""

    # owner test
    response = client.post(
        f"/projects/{mockproject.name}/tasks/{mock_discrete_task.name}/members/{user3.username}",
        headers={"content-type": "application/json", "token-uuid": token1},
    )

    assert response.status_code == 200
    assert response.json()["detail"] == "Member added to the task successfully"

    # moderator test
    response = client.post(
        f"/projects/{mockproject.name}/tasks/{mock_milestone_task.name}/members/{user3.username}",
        headers={"content-type": "application/json", "token-uuid": token2},
    )

    assert response.status_code == 200
    assert response.json()["detail"] == "Member added to the task successfully"

    # admin test
    response = client.post(
        f"/projects/{mockproject.name}/tasks/{extra_discrete_task.name}/members/{user3.username}",
        headers={"content-type": "application/json", "token-uuid": admin_token},
    )

    assert response.status_code == 200
    assert response.json()["detail"] == "Member added to the task successfully"


def test_add_nonexisting_member() -> None:
    """Try adding a user that is not part of the project to the task"""

    response = client.post(
        f"/projects/{mockproject.name}/tasks/{extra_discrete_task.name}/members/nonexistinguser",
        headers={"content-type": "application/json", "token-uuid": token1},
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "User is not part of the project. Add them as a member of the project first!"
    )


def test_remove_nonexisting_member() -> None:
    """Try removing a user from a task that they are not part of"""

    response = client.delete(
        f"/projects/{mockproject.name}/tasks/{extra_discrete_task.name}/members/nonexistinguser",
        headers={"content-type": "application/json", "token-uuid": token1},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User is not part of the task"


def test_update_task_completion() -> None:
    """Test updating task completion as all user levels, for all task types"""

    # member test, discrete task
    response = client.put(
        f"/projects/{mockproject.name}/tasks/{mock_discrete_task.name}/completion?completion=true",
        headers={"content-type": "application/json", "token-uuid": token3},
    )

    assert response.status_code == 200
    assert response.json()["detail"] == "Task completion updated successfully"

    # moderator test, milestone task
    response = client.put(
        f"/projects/{mockproject.name}/tasks/{mock_milestone_task.name}/completion?completion=3",
        headers={"content-type": "application/json", "token-uuid": token2},
    )

    assert response.status_code == 200
    assert response.json()["detail"] == "Task completion updated successfully"

    # admin test, milestone task
    response = client.put(
        f"/projects/{mockproject.name}/tasks/{mock_milestone_task.name}/completion?completion=5",
        headers={"content-type": "application/json", "token-uuid": admin_token},
    )

    assert response.status_code == 200
    assert response.json()["detail"] == "Task completion updated successfully"

    # owner test, discrete task
    response = client.put(
        f"/projects/{mockproject.name}/tasks/{extra_discrete_task.name}/completion?completion=true",
        headers={"content-type": "application/json", "token-uuid": token1},
    )

    assert response.status_code == 200
    assert response.json()["detail"] == "Task completion updated successfully"


def test_remove_member() -> None:
    """Test removing users from tasks as owner, moderator and admin"""

    # owner test
    response = client.delete(
        f"/projects/{mockproject.name}/tasks/{mock_discrete_task.name}/members/{user3.username}",
        headers={"content-type": "application/json", "token-uuid": token1},
    )

    assert response.status_code == 200
    assert response.json()["detail"] == "User removed from task successfully"

    # moderator test
    response = client.delete(
        f"/projects/{mockproject.name}/tasks/{mock_milestone_task.name}/members/{user3.username}",
        headers={"content-type": "application/json", "token-uuid": token2},
    )

    assert response.status_code == 200
    assert response.json()["detail"] == "User removed from task successfully"

    # admin test
    response = client.delete(
        f"/projects/{mockproject.name}/tasks/{extra_discrete_task.name}/members/{user3.username}",
        headers={"content-type": "application/json", "token-uuid": admin_token},
    )

    assert response.status_code == 200
    assert response.json()["detail"] == "User removed from task successfully"


def test_remove_task_unauthorized() -> None:
    """Try removing a task as a mere member"""

    response = client.delete(
        f"/projects/{mockproject.name}/tasks/{mock_discrete_task.name}",
        headers={"content-type": "application/json", "token-uuid": token3},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You cannot modify tasks within this project"


def test_remove_nonexisting_task() -> None:
    """Try to remove a task that does not exist"""

    response = client.delete(
        f"/projects/{mockproject.name}/tasks/randomtaskthatdoesnotexist",
        headers={"content-type": "application/json", "token-uuid": token1},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_remove_task() -> None:
    """Test removing tasks as owner, moderator and admin"""

    # owner test
    response = client.delete(
        f"/projects/{mockproject.name}/tasks/{mock_discrete_task.name}",
        headers={"content-type": "application/json", "token-uuid": token1},
    )

    assert response.status_code == 200
    assert response.json()["detail"] == "Task deleted successfully"

    # moderator test
    response = client.delete(
        f"/projects/{mockproject.name}/tasks/{mock_milestone_task.name}",
        headers={"content-type": "application/json", "token-uuid": token2},
    )

    assert response.status_code == 200
    assert response.json()["detail"] == "Task deleted successfully"

    # admin test
    response = client.delete(
        f"/projects/{mockproject.name}/tasks/{extra_discrete_task.name}",
        headers={"content-type": "application/json", "token-uuid": admin_token},
    )

    assert response.status_code == 200
    assert response.json()["detail"] == "Task deleted successfully"
