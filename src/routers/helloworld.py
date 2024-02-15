from fastapi import APIRouter, Request, HTTPException
import sys

sys.path.append("../src")
from database import db
from src.models import Token, Token_DB

router = APIRouter()


@router.get("/")
def hello(request: Request) -> dict:
    """Simple Hello World API call

    Args:
        request (Request): header should contain "token" token

    Returns:
        dict: server response
    """
    # get token from request body and check if it's in the database
    token = request.headers["token"]
    query = db.sessions.find_one({"token": token})
    if query == None:
        raise HTTPException(403, "Unauthorized access")

    # validate token from db
    try:
        token = Token_DB(**query)
    except:
        raise HTTPException(502, "Something went wrong when checking session token")

    if token.check_alive() == False:
        raise HTTPException(403, "Unauthorized access")

    return {"response": "hello there!"}
