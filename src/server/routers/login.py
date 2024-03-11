# global imports
from fastapi import APIRouter, HTTPException, Depends, Body

# relative imports
from ..dependencies import db_depend
from ..models import Token
from ..database import Database

router = APIRouter()


@router.post("/login/")
def login(
    username: str = Body(), password: str = Body(), db: Database = Depends(db_depend)
) -> Token:
    """Login endpoint

    Args:
        username (str): account username, included in body
        password (str): account hashed password, included in body

    Returns:
        Token: session token
    """

    # find user data in database, then compare username and password provided
    user_db = db.get_user_db(username)

    if user_db is None or password != user_db.password:
        raise HTTPException(401, "Incorrect username or password")

    # if the user already has a session token in the database, delete it
    user_id = db.get_user_id(username)
    token_query = db.get_token_by_user(user_id)
    if token_query is not None:
        db.delete_token(token_query.token)

    # generate token, then add it to database
    token = Token.generate(username)
    rc = db.post_token(token, user_id)

    if rc is False:
        raise HTTPException(500, "Could not log in")
    return token
