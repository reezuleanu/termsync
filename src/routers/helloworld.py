# global imports
from fastapi import APIRouter, Request, HTTPException
from uuid import UUID
import sys

# relative imports
sys.path.append("../src")
from database import authorize_token
from src.models import Token

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

    # validate token data
    try:
        token = UUID(token)
        token = Token(token=token)
    except TypeError:
        raise HTTPException(406, "invalid request")

    if not authorize_token(token):
        raise HTTPException(403, "Unauthorized access")

    return {"response": "hello there!"}
