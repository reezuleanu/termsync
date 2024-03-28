"""Project endpoints dependencies"""

from fastapi import Depends, HTTPException
from .db_depend import db_depend
from .token_auth import token_auth, admin_auth
from ..models import Project, User
from ..database import Database


def project_depend(
    project_name: str,
    user: User = Depends(token_auth),
    db: Database = Depends(db_depend),
    admin: bool = Depends(admin_auth),
) -> Project:

    # check if project exists
    project = db.get_project(project_name)

    if project is None:
        raise HTTPException(404, "Project not found")

    # check if user has sufficient permissions to view project
    # user_id = db.get_user_id(user.username)

    if user.username not in project.members and admin is False:
        raise HTTPException(403, "You are not a member of this project")

    return project


def task_depend(
    task_name: str,
    project: Project = Depends(project_depend),
    user: User = Depends(token_auth),
    db: Database = Depends(db_depend),
    admin: bool = Depends(admin_auth),
) -> None:
    raise NotImplementedError
