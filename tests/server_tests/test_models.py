# global imports
from datetime import datetime, timedelta
from uuid import UUID
from bson import ObjectId

# relative imports
# sys.path.append("../src")
from src.server.models import (
    Token,
    Token_DB,
    Task,
    User,
    Project,
    Discrete_Task,
    Milestone_Task,
)


### TOKENS ###


def test_token_generate() -> None:
    """Test token generation"""

    token = Token.generate("username")
    assert token


def test_token_validate() -> None:
    """Test token validation"""

    token = Token_DB(
        token="8a488bfe-c67b-5593-a97e-4a80bf081aa4",
        user_id=ObjectId("65c77de92ab5ae955858182c"),
        expiration=datetime.now() + timedelta(hours=72),
    )
    assert token
    assert token.token == "8a488bfe-c67b-5593-a97e-4a80bf081aa4"
    assert token.check_alive()

    # expired token

    token.expiration = datetime.now() - timedelta(hours=72)

    assert token.check_alive() == False


### TASKS ###


def test_task_add_member() -> None:
    """Test adding members to task"""

    task = Task(name="Test task")
    user1 = User(username="ranomdusername1", full_name="randomfullname1")
    user2 = User(username="ranomdusername2", full_name="randomfullname2")

    # successful add
    assert task.add_member(user1, user2)
    assert user1, user2 in task.members

    # add duplicate
    user3 = User(username="ranomdusername3", full_name="randomfullname3")

    assert task.add_member(user2, user3) == False
    assert user3 in task.members


def test_task_remove_member() -> None:
    """Test removing members from task"""

    task = Task(name="Test task")
    user1 = User(username="ranomdusername1", full_name="randomfullname1")
    user2 = User(username="ranomdusername2", full_name="randomfullname2")

    task.add_member(user1, user2)

    # successful removal
    assert task.remove_member(user1)
    assert user1 not in task.members and user2 in task.members

    # not_found failed removal
    assert task.remove_member(user1) == False
    assert user2 in task.members


def test_milestone_task() -> None:
    """Test milestone task functionality"""

    task = Milestone_Task(name="milestone task", milestones=22)

    assert task
    assert task.milestones == 22
    assert task.completed == 0
    assert task.percentage_completed == 0

    task.completed = 11
    assert task.percentage_completed == 50


def test_discrete_task() -> None:
    """Test discrete task functionality"""

    task = Discrete_Task(name="discrete task")

    assert task
    assert task.completed == False

    task.completed = True
    assert task.completed


### PROJECTS ###


def test_project_task() -> None:
    """Test functionality of project tasks"""

    project = Project(name="test project")

    task1 = Discrete_Task(name="Test task 1", completed=True)
    task2 = Milestone_Task(name="test task 2", milestones=40, completed=21)

    # test adding tasks
    assert project.add_task(task1)
    assert project.add_task(task2)
    assert task1 in project.tasks and task2 in project.tasks

    # test add duplicate tasks
    assert project.add_task(task1) == False

    # test remove tasks

    assert project.remove_task(task1)
    assert task1 not in project.tasks and task2 in project.tasks

    # test removing unexisting tasks

    assert project.remove_task(task1) == False
    assert task2 in project.tasks


def test_project_member() -> None:
    """Test functionality of project members"""

    project = Project(name="test project")

    user1 = User(username="ranomdusername1", full_name="randomfullname1")
    user2 = User(username="ranomdusername2", full_name="randomfullname2")

    # test add members

    assert project.add_member(user1, user2)
    assert user1, user2 in project.members

    # test add duplicate members

    assert project.add_member(user1) == False
    assert user1, user2 in project.members

    # test remove members

    assert project.remove_member(user1)
    assert user1 not in project.members and user2 in project.members

    # test remove nonexisting member

    assert project.remove_member(user1) == False
    assert user2 in project.members
