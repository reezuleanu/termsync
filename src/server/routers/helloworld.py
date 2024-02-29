# global imports
from fastapi import APIRouter, Request, HTTPException, Depends, Body
from uuid import UUID

# relative imports
from ..database import authorize_token
from ..models import Token
from ..dependencies import token_auth

router = APIRouter()


@router.get("/")
def hello(token: Token = Depends(token_auth)) -> dict:
    """Simple Hello World API call

    Args:
        token (Token): User Token.

    Returns:
        dict: API response
    """

    return {"response": "hello there!", "token": token}
