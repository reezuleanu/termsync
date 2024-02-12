# global imports
from fastapi import HTTPException, APIRouter
import sys

# relative imports
sys.path.append("../")
from models import User, User_DB
from utils import bson2dict, result_get_id
from bson import ObjectId
from database import db


router = APIRouter()


@router.post("/user/")
def create_user(data: dict[str, User | str]) -> User:
    """Call which creates a user in the database

    Args:
        data (dict[User, str]): user submitted data, the dictionary contains the user data, then the hashed password

    Returns:
        User: user data, now containing the database ID
    """
    # check if there already is a user with that username
    user_data = data["user"].model_dump()
    password = data["password"]
    if db.users.find_one({"username": user_data["username"]}) != None:
        raise HTTPException(406, "username already taken")

    # create appropriate class for the db then inser it
    user_db = User_DB(password=password, **user_data)
    request = db.users.insert_one(user_db.model_dump())
    if request.acknowledged == True:
        # convert _id from bson to string
        id = result_get_id(request)
        user_data["id"] = id  # overwrite user_data value for id
        user = User(**user_data)
        return user
    else:
        raise HTTPException(500, "could not create user")


@router.delete("/user/")
def delete_user(data: dict[str, str]) -> dict:
    """Call which deletes a user from the database. Requires password for confirmation

    Args:
        data (dict[str, str]): dictionary containing user id in the database and hashed password

    Returns:
        dict: server response
    """
    # ObjectId validation
    try:
        id = ObjectId(data["id"])
    except:
        raise HTTPException(406, "invalid id")

    query = db.users.find_one({"_id": id})
    if query == None:
        raise HTTPException(404, "could not find user")

    query_data = bson2dict(query)
    password = data["password"]

    if query_data["password"] != password:
        raise HTTPException(406, "incorrect password")

    request = db.users.delete_one(query)
    if request.acknowledged == True:
        raise HTTPException(200, "user deleted successfully")
    else:
        raise HTTPException(500, "could not delete user from database")


@router.get("/user/")
# def get_user(data: dict[str, str]) -> User:
def get_user(username: str) -> User:
    """Call which returns user data

    Args:
        data (dict[str, str]): dictionary containing the username of the user to retrieve data of

    Returns:
        User: data retrieved from database
    """
    data = username
    request = db.users.find_one({"username": data})
    if request == None:
        raise HTTPException(404, "could not find user")
    user_data = bson2dict(request)
    try:
        user = User(
            **user_data
        )  # if this fails, it means corrupted data got in the database somehow
    except:
        raise HTTPException(500, "corrupted user data")
    return user


@router.put("/user/")
def update_user(data: User) -> User:

    # pull the user from the database to check if the username is different or not
    user_data = data.model_dump()
    user_id = ObjectId(user_data["id"])
    query = db.users.find_one({"_id": user_id})

    if query == None:
        raise HTTPException(404, "could not find user")

    user_db_data = bson2dict(query)
    if user_data["username"] != user_db_data["username"]:
        raise HTTPException(406, "you cannot change your username")

    # remove id attribute do avoid conflict with db class
    user_data.pop("id")
    update_data = {"$set": user_data}
    if db.users.update_one({"_id": user_id}, update_data).acknowledged == True:
        return User(**bson2dict(db.users.find_one({"_id": user_id})))
    else:
        raise HTTPException(500, "could not update user data")
