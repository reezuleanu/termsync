from fastapi import APIRouter, HTTPException
import sys

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

    if query == None:
        raise HTTPException(401, "Incorrect username or password")
    query = bson2dict(query)
    if query["password"] != password:
        raise HTTPException(401, "Incorrect username or password")

    token = Token.generate()

    return token
