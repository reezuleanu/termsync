# global imports
from fastapi import APIRouter, HTTPException
import sys

# relative imports
sys.path.append("../")
from database import db
from utils import bson2dict
from models import Token

router = APIRouter()


@router.get("/login/")
def get_login(data: dict[str, str]) -> Token:
    # get details from request body
    username = data["username"]
    password = data["password"]

    # find user data in database, then compare username and password provided
    query = db.users.find_one({"username": username})

    if query is None:
        raise HTTPException(401, "Incorrect username or password")
    query = bson2dict(query)
    if query["password"] != password:
        raise HTTPException(401, "Incorrect username or password")

    # generate token, then add it to database
    token = Token.generate(username)

    # convert the database id to a plain string because i have had it with the
    # way mongodb stores objects
    token = token.convert(user_id=str(query["_id"]["$oid"]))

    if db.sessions.insert_one(token.model_dump()).acknowledged is False:
        raise HTTPException(502, "could not add session token to the database")
    return token
