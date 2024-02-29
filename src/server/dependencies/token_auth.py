# get token from request body and check if it's in the database
from uuid import UUID
from fastapi import HTTPException, Header, Depends

from ..models import Token


def token_auth(token: UUID = Header()) -> Token:
    """Token Authentification dependency

    Args:
        token (UUID): User token
    """
    # simple token validation
    token = Token(token=token)
    if isinstance(token, Token):
        return token
    else:
        raise HTTPException(401)
