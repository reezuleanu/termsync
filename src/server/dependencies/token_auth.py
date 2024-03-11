from uuid import UUID
from fastapi import HTTPException, Header, Depends

from ..models import User
from ..database import Database
from .db_depend import db_depend


def token_auth(token_uuid: UUID = Header(), db: Database = Depends(db_depend)) -> User:
    """Token Authentification dependency, returns user data to be used by functions

    Args:
        token (UUID): User token in request header

    Returns:
        user (User): User data from the database
    """

    # get token from database
    token = db.get_token(token_uuid)
    if token is None:
        raise HTTPException(401, "Token not found")

    # check if it's expired
    if not token.check_alive():
        db.delete_token(token_uuid)  # delete the expired token
        raise HTTPException(401, "Token is expired")

    user = db.get_user(token.user_id)

    if user is None:
        raise HTTPException(500, "User not in database")

    return user


def admin_auth(token_uuid: UUID = Header(), db: Database = Depends(db_depend)) -> bool:
    """Dependency that checks if the user is an administrator or not

    Args:
        token_uuid (UUID, optional): _description_. Defaults to Header().
        db (Database, optional): _description_. Defaults to Depends(db_depend).

    Raises:
        HTTPException: _description_
    """

    # no longer doing checks since it's already handled by token_auth

    user_db = db.get_user_db(db.get_token(token_uuid).user_id)

    if user_db.power != "admin":
        return False
    return True
