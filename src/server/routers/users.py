# global imports
from fastapi import HTTPException, APIRouter, Body, Depends

# relative imports
from ..models import User, User_DB, Token
from ..database import Database

from ..dependencies import db_depend, token_auth, admin_auth


router = APIRouter()


@router.post("/users/")
def create_user(
    user: User, password: str = Body(), db: Database = Depends(db_depend)
) -> Token:
    """Create user in the database and return a session token for that user

    Args:
        user (User): user data
        password (str): hashed password


    Returns:
        Token: session token for the newly created user
    """

    # check if there already is a user with that username
    user_data = user.model_dump()

    if db.get_user(user_data["username"]) is not None:
        raise HTTPException(406, "Username already taken")

    # create appropriate class for the db then insert it
    user_db = User_DB(password=password, **user_data)
    rc, user_id = db.post_user(user_db)

    if rc is False:
        raise HTTPException(500, "Could not create user")

    # create session token and return it
    token = Token.generate(user_data["username"])

    if db.post_token(token, user_id) is False:
        raise HTTPException(500, "Could not create session token")

    return token


@router.delete("/users/{username}")
def delete_user(
    username: str,
    user: User = Depends(token_auth),
    password: str = Body(),
    db: Database = Depends(db_depend),
    admin: bool = Depends(admin_auth),
) -> dict:
    """Delete user from the database. Requires password for confirmation

    Args:
        username (str): username of the account to be deleted
        password (str): password of the account to be deleted


    Returns:
        dict: API response
    """

    # query = db.get_user_by_username(username)
    user_db = db.get_user_db(username)
    if user_db is None:
        raise HTTPException(404, "Could not find user")

    if user.username != user_db.username and admin is False:
        raise HTTPException(401, "You cannot delete someone else's account")

    if password != user_db.password and admin is False:
        raise HTTPException(401, "Incorrect password")

    rc = db.delete_user(username)

    if rc is False:
        raise HTTPException(500, "Could not delete user from database")

    return {"detail": "User deleted successfully"}


@router.get("/users/{username}")
def get_user(
    username: str, user: User = Depends(token_auth), db: Database = Depends(db_depend)
) -> User:
    """Call that returns user data by username

    Args:
        username (str): exact username

    Returns:
        User: User data
    """

    # query = db.get_user_by_username(username)
    query = db.get_user(username)

    if query is None:
        raise HTTPException(404, "User not found")

    return query


@router.get("/users/")
def search_users(
    search: str, user: User = Depends(token_auth), db: Database = Depends(db_depend)
) -> list[str]:

    query = db.search_users(search)

    if query is None:
        raise HTTPException(404, "Could not find any users with that search")

    response = []
    for user in query:
        response.append(user["username"])

    return response


@router.put("/users/{username}")
def update_user(
    username: str,
    user_data: User,
    user: User = Depends(token_auth),
    db: Database = Depends(db_depend),
    admin: bool = Depends(admin_auth),
) -> dict:
    """Modify user data

    Args:
        user_data (User): updated user data
        username (str): username of account to be modified

    Returns:
        bool: API response
    """

    if username != user.username and admin is False:
        raise HTTPException(401, "You cannot modify another user's account")

    # the username is unique, check if the user tries to change it
    if user_data.username != username:
        raise HTTPException(400, "You cannot change the username")

    # check if the user is in the database (useful for when an admin tries to change someone's data)
    if db.get_user(username) is None:
        raise HTTPException(404, "User not found")

    if db.update_user(user_data, username) is False:
        raise HTTPException(500, "Could not update user")

    return {"detail": "User updated successfully"}


@router.post("/admin/{username}")
def make_admin(
    username: str,
    user: User = Depends(token_auth),
    db: Database = Depends(db_depend),
    admin: bool = Depends(admin_auth),
) -> dict:
    """Make a user an admin (must be an admin yourself)

    Args:
        username (str): username of user to be made admin

    Returns:
        dict: API response
    """

    if admin is False:
        raise HTTPException(401, "You must be an admin to use this command")

    # check if user exists
    if db.get_user(username) is None:
        raise HTTPException(404, "User does not exist")

    if db.make_admin(username) is False:
        raise HTTPException(500, "Could not make user an admin")

    return {"detail": "User promoted to admin successfully"}
