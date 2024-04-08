# global imports
from fastapi import APIRouter, HTTPException, Request, Depends, Body
from pydantic import ValidationError


# relative imports
from ..models import Project, User, Discrete_Task, Milestone_Task
from ..dependencies import token_auth, admin_auth, db_depend, project_depend
from ..database import Database


router = APIRouter()


@router.post("/projects/")
def add_project(
    project: Project,
    user: User = Depends(token_auth),
    db: Database = Depends(db_depend),
) -> dict:
    """Add project to the database

    Args:
        project (Project): Project data

    Returns:
        dict: API response
    """

    # check if project already exists
    if db.get_project(project.name) is not None:
        raise HTTPException(403, "Project already exists")

    # add owner
    project.owner = user.username
    project.members.append(user.username)

    # ! DEPRECATED
    # convert usernames to ids
    # project.convert(db)

    # add project
    response = db.add_project(project)
    if response is False:
        raise HTTPException(503, "Could not add project to database")

    # return project to client
    return {"detail": "Project created successfully"}


@router.get("/projects/{project_name}")
def get_project(
    project: Project = Depends(project_depend), db: Database = Depends(db_depend)
) -> Project:
    """Get project from the database (projects can be viewed only by members or admins)

    Args:
        project_name(str): Taken by project_depend from URL. It returns the project if the user
        can view it (is a member or admin)
        project (Project): Project data returned by project_depend

    Returns:
        Project: Project data
    """

    # ! DEPRECATED
    # convert ids to usernames
    # project.render(db)

    return project


@router.get("/projects/all/")
def get_all_projects(
    user: User = Depends(token_auth), db: Database = Depends(db_depend)
) -> dict:

    # get all projects user is a member of
    query = db.get_all_project(user.username)
    if query is None:
        raise HTTPException(404, "Could not find any projects")

    response = {}
    for project in query:
        project = Project(**project)
        response[project.name] = project.progress

    return response


@router.put("/projects/{project_name}")
def update_project(
    updated_project: Project,
    project: Project = Depends(project_depend),
    user: User = Depends(token_auth),
    db: Database = Depends(db_depend),
    admin: bool = Depends(admin_auth),
) -> dict:
    """Update project data (except name). Only the owner of the project or an admin can use this

    Args:
        updated_project (Project): Updated project data
        project (Project): Project data returned by project_depend if user is a member of the project (or admin)

    Returns:
        dict: API response
    """

    # check if the user can modify the project
    if user.username != project.owner and admin is False:
        raise HTTPException(403, "You cannot modify a project you are not the owner of")

    # check if user is trying to change the name of the project
    if updated_project.name != project.name:
        raise HTTPException(400, "Cannot modify project name")

    # modify project
    request = db.update_project(project.name, updated_project)

    if request is False:
        raise HTTPException(500, "Could not modify project")

    return {"detail": "Project updated successfully"}


@router.delete("/projects/{project_name}")
def delete_project(
    project: Project = Depends(project_depend),
    user: User = Depends(token_auth),
    db: Database = Depends(db_depend),
    admin: bool = Depends(admin_auth),
) -> dict:
    """Delete project from the database, can only be done by the owner or an admin

    Args:
        project (Project): Project data returned by project_depend if user is a member of the project (or admin)

    Returns:
        dict: API response
    """

    # check if user can delete the project
    if user.username != project.owner and admin is False:
        raise HTTPException(403, "Cannot delete a project you are not a owner of")

    # delete project
    if db.delete_project(project.name) is False:
        raise HTTPException(500, "could not delete project")

    return {"detail": "project deleted successfully"}


@router.post("/projects/{project_name}/members/{member_username}")
def add_project_member(
    member_username: str,
    project: Project = Depends(project_depend),
    user: User = Depends(token_auth),
    db: Database = Depends(db_depend),
    admin: bool = Depends(admin_auth),
) -> dict:

    # check if user can add members to project
    if (
        user.username != project.owner
        and user.username not in project.moderators
        and admin is False
    ):
        raise HTTPException(403, "You cannot add members to this project")

    # check if member to add is already in project
    if member_username in project.members:
        raise HTTPException(400, "User already part of project")

    # check if member exists
    if db.get_user(member_username) is None:
        raise HTTPException(404, "User does not exist")

    # add member to project
    project.add_member(member_username)

    if db.update_project(project.name, project) is False:
        raise HTTPException(500, "Could not add user to project")

    return {"detail": "User added to project successfully"}


@router.delete("/projects/{project_name}/members/{member_username}")
def remove_project_member(
    member_username: str,
    project: Project = Depends(project_depend),
    user: User = Depends(token_auth),
    db: Database = Depends(db_depend),
    admin: bool = Depends(admin_auth),
) -> dict:

    # check if user can remove members from project
    if (
        user.username != project.owner
        and user.username not in project.moderators
        and admin is False
    ):
        raise HTTPException(403, "You cannot remove members from this project")

    # check if member to remove is  in project
    if member_username not in project.members:
        raise HTTPException(404, "User is not part of the project")

    # delete member
    project.remove_member(member_username)

    if db.update_project(project.name, project) is False:
        raise HTTPException(500, "Could not remove user from project")

    return {"detail": "User removed from project successfully"}


@router.post("/projects/{project_name}/moderators/{member_username}")
def add_project_moderator(
    member_username: str,
    project: Project = Depends(project_depend),
    user: User = Depends(token_auth),
    db: Database = Depends(db_depend),
    admin: bool = Depends(admin_auth),
) -> dict:

    # check if user can add moderators to the project
    if user.username != project.owner and admin is False:
        raise HTTPException(403, "You cannot add moderators to this project")

    # check if user to be made moderator is part of project
    if member_username not in project.members:
        raise HTTPException(
            404,
            "User is not a member of the project. Add them before making them a moderator",
        )

    # make user moderator
    project.add_moderator(member_username)

    if db.update_project(project.name, project) is False:
        raise HTTPException(500, "Could not make user a moderator")

    return {"detail": "Moderator added successfully"}


@router.delete("/projects/{project_name}/moderators/{member_username}")
def remove_project_moderator(
    member_username: str,
    project: Project = Depends(project_depend),
    user: User = Depends(token_auth),
    db: Database = Depends(db_depend),
    admin: bool = Depends(admin_auth),
) -> dict:

    # check if user can remove moderators from the project
    if user.username != project.owner and admin is False:
        raise HTTPException(403, "You cannot remove moderators from this project")

    # check if user to be demoted is a moderator
    if member_username not in project.moderators:
        raise HTTPException(
            404,
            "User is not a moderator in this project",
        )

    # demote user

    project.remove_moderator(member_username)

    if db.update_project(project.name, project) is False:
        raise HTTPException(500, "Could not demote moderator")

    return {"detail": "User demoted successfully"}


@router.post("/projects/{project_name}/tasks/")
def add_task(
    project_name: str,
    task: Discrete_Task | Milestone_Task,
    user: User = Depends(token_auth),
    db: Database = Depends(db_depend),
    admin: bool = Depends(admin_auth),
) -> dict:

    # check if project exists
    project = db.get_project(project_name)
    if project is None:
        raise HTTPException(404, "Project not found")

    # check if user can add task
    if (
        user.username != project.owner
        and user.username not in project.moderators
        and admin is False
    ):
        raise HTTPException(403, "You are not authorized to add tasks to this project")

    if project.add_task(task) is False:
        raise HTTPException(401, "Could not add task to project. Task already exists.")

    if db.update_project(project_name, project) is False:
        raise HTTPException(500, "Could not add task to project")

    return {"detail": "Task added successfully"}


@router.put("/projects/{project_name}/tasks/{task_name}")
def update_task(
    task_name: str,
    updated_task: Discrete_Task | Milestone_Task,
    project: Project = Depends(project_depend),
    user: User = Depends(token_auth),
    db: Database = Depends(db_depend),
    admin: bool = Depends(admin_auth),
) -> dict:

    # check if user has sufficient permissions to modify task
    if (
        user.username != project.owner
        and user.username not in project.moderators
        and admin is False
    ):
        raise HTTPException(403, "You cannot modify tasks within this project")

    # check if task exists
    if task_name not in [task.name for task in project.tasks]:
        raise HTTPException(404, "Task not found")

    # check if the user is trying to modify the name of the task
    if updated_task.name != task_name:
        raise HTTPException(406, "You cannot change the name of the task")

    # modify task
    task_index = [task.name for task in project.tasks].index(task_name)

    project.tasks[task_index] = updated_task

    if db.update_project(project.name, project) is False:
        raise HTTPException(500, "Could not modify task")

    return {"detail": "Task updated successfully"}


@router.delete("/projects/{project_name}/tasks/{task_name}")
def delete_task(
    task_name: str,
    project: Project = Depends(project_depend),
    user: User = Depends(token_auth),
    db: Database = Depends(db_depend),
    admin: bool = Depends(admin_auth),
) -> dict:
    """Delete task from project

    Args:
        project_name (str): Name of project containing the task
        task_name (str): Name of task to be deleted

    Returns:
        dict: API response
    """

    # check if user has sufficient permissions to modify task
    if (
        user.username != project.owner
        and user.username not in project.moderators
        and admin is False
    ):
        raise HTTPException(403, "You cannot modify tasks within this project")

    # check if task exists
    if task_name not in [task.name for task in project.tasks]:
        raise HTTPException(404, "Task not found")

    # delete task and update project
    task_index = [task.name for task in project.tasks].index(task_name)
    project.tasks.pop(task_index)

    if db.update_project(project.name, project) is False:
        raise HTTPException(500, "Could not delete task")

    return {"detail": "Task deleted successfully"}


@router.put("/projects/{project_name}/tasks/{task_name}/completion")
def update_task_completion(
    task_name: str,
    completion: bool | int,
    project: Project = Depends(project_depend),
    user: User = Depends(token_auth),
    db: Database = Depends(db_depend),
    admin: bool = Depends(admin_auth),
) -> dict:

    # check if task exists
    if task_name not in [task.name for task in project.tasks]:
        raise HTTPException(404, "Task does not exist")

    task_index = [task.name for task in project.tasks].index(task_name)

    # check if user can modify the task completion
    if (
        user.username != project.owner
        and user.username not in project.moderators
        and user.username not in project.tasks[task_index].members
        and admin is False
    ):
        raise HTTPException(
            403, "You are not allowed to change the completion of this task"
        )

    # modify task completion
    if type(project.tasks[task_index].completed) is not type(completion):
        raise HTTPException(400, "Wrong type of completion for task type")

    project.tasks[task_index].completed = completion

    if db.update_project(project.name, project) is False:
        raise HTTPException(500, "Could not update task completion")

    return {"detail": "Task completion updated successfully"}


@router.post("/projects/{project_name}/tasks/{task_name}/members/{member_username}")
def add_task_member(
    task_name: str,
    member_username: str,
    project: Project = Depends(project_depend),
    user: User = Depends(token_auth),
    db: Database = Depends(db_depend),
    admin: bool = Depends(admin_auth),
) -> dict:

    # check if user can add a member
    if (
        user.username != project.owner
        and user.username not in project.moderators
        and admin is False
    ):
        raise HTTPException(
            403, "You are not allowed to add members to tasks in this project"
        )

    # check if task exists
    if task_name not in [task.name for task in project.tasks]:
        raise HTTPException(404, "Task does not exist")

    task_index = [task.name for task in project.tasks].index(task_name)

    # check if member is part of the project
    if member_username not in project.members:
        raise HTTPException(
            400,
            "User is not part of the project. Add them as a member of the project first!",
        )

    # add member to task
    project.tasks[task_index].add_member(member_username)

    if db.update_project(project.name, project) is False:
        raise HTTPException(500, "Could not add user to task")

    return {"detail": "Member added to the task successfully"}


@router.delete("/projects/{project_name}/tasks/{task_name}/members/{member_username}")
def remove_task_member(
    task_name: str,
    member_username: str,
    project: Project = Depends(project_depend),
    user: User = Depends(token_auth),
    db: Database = Depends(db_depend),
    admin: bool = Depends(admin_auth),
) -> dict:

    # check if user can remove a member
    if (
        user.username != project.owner
        and user.username not in project.moderators
        and admin is False
    ):
        raise HTTPException(
            403, "You are not allowed to add members to tasks in this project"
        )

    # check if task exists
    if task_name not in [task.name for task in project.tasks]:
        raise HTTPException(404, "Task does not exist")

    task_index = [task.name for task in project.tasks].index(task_name)

    # check if member is part of the task
    if member_username not in project.tasks[task_index].members:
        raise HTTPException(
            400,
            "User is not part of the task",
        )

    # remove user from task
    project.tasks[task_index].remove_member(member_username)

    if db.update_project(project.name, project) is False:
        raise HTTPException(500, "Could not remove user from task")

    return {"detail": "User removed from task successfully"}


@router.get("/update/projects")
def update_projects(
    user: User = Depends(token_auth), db: Database = Depends(db_depend)
) -> list:

    user_data = db.get_user_db(user.username)

    if user_data is None:
        raise HTTPException(404, "Could not find user")

    updated_projects = user_data.update_projects

    user_data.update_projects = []

    if db.update_user(user_data, user.username) is False:
        raise HTTPException(500)

    return updated_projects
