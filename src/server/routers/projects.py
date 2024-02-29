# global imports
from fastapi import APIRouter, HTTPException, Request
from pydantic import ValidationError


# relative imports
from ..models import Project
from ..database import db, authorize_token
from ..utils import result_get_id, bson2dict

router = APIRouter()


@router.post("/projects/")
def add_project(request: Request, data: dict[str, Project]) -> Project:

    # token validation part
    token = request.headers["token"]

    token = validate_token(token)

    if token is False:
        raise HTTPException(406)

    if authorize_token(token) is False:
        raise HTTPException(403)

    # project validation part

    try:
        project = data["project"]
    except ValidationError:
        raise HTTPException(406)

    # check if project already exists

    if db.projects.find_one({"name": project.name}) != None:
        raise HTTPException(403, "project already exists")

    response = db.projects.insert_one(project.model_dump())
    if response.acknowledged == False:
        raise HTTPException(503, "could not add project to database")

    project.id = result_get_id(response)

    if (
        db.projects.update_one(
            {"name": project.name}, {"$set": {"id": project.id}}
        ).acknowledged
        == False
    ):
        raise HTTPException(503, "could not add project to database")

    return project


@router.get("/projects/")
def get_project() -> Project:
    pass


@router.put("/projects/")
def update_project(request: Request, data: dict[str, Project]) -> Project:

    # token validation part
    token = request.headers["token"]

    token = validate_token(token)

    if token is False:
        raise HTTPException(406)

    token_db = authorize_token(token)

    if token_db is False:
        raise HTTPException(403)

    project = data["project"]

    # check if project exists

    query = db.projects.find_one({"name": project.name})
    if query == None:
        raise HTTPException(404)

    # check if user can modify project
    project = Project(**bson2dict(query))

    if token_db.user_id != project.owner_id:
        raise HTTPException(403, "you are not the owner of this project")

    # modify the project

    if (
        db.projects.update_one(
            {"name": project.name}, {"$set": project.model_dump()}
        ).acknowledged
        == False
    ):
        raise HTTPException(500, "could not modify project")

    return project


@router.delete("/projects/")
def delete_project(request: Request, data: dict[str, str]) -> dict:

    # token validation part
    token = request.headers["token"]

    token = validate_token(token)

    if token is False:
        raise HTTPException(406)

    token_db = authorize_token(token)

    if token_db is False:
        raise HTTPException(403)

    # check if project exists
    project_id = data["id"]

    query = db.projects.find_one({"id": project_id})
    if query == None:
        raise HTTPException(404)

    # check if user can delete the project
    project = Project(**bson2dict(query))

    if token_db.user_id != project.owner_id:
        raise HTTPException(403, "you are not the owner of this project")

    if db.projects.delete_one({"id": project_id}).acknowledged == False:
        raise HTTPException(500, "could not delete project")

    return {"detail": "project deleted successfully"}
