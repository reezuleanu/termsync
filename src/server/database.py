# global imports
from pymongo import MongoClient, cursor
from uuid import UUID
from bson import ObjectId
from typing import Union, List
import os

# relative imports
from .models import Token, Token_DB, User, User_DB, Project

try:
    DB_HOST = os.environ["PYMONGO_DATABASE_HOST"]
    DB_PORT = int(os.environ["PYMONGO_DATABASE_PORT"])
except KeyError:
    DB_HOST = "127.0.0.1"
    DB_PORT = 27017


class Database:
    """Pymongo database interface class"""

    def __init__(self) -> None:
        self.client = MongoClient(host=DB_HOST, port=DB_PORT)
        self.db = self.client.termsync

    # USER METHODS
    def get_user(self, user: str | ObjectId) -> User:
        """Method that gets user data from database by username or id

        Args:
            user_id (str | ObjectId): username or user id

        Returns:
            User: user data
        """

        if type(user) is str:
            query = self.db.users.find_one({"username": user})
        if type(user) is ObjectId:
            query = self.db.users.find_one({"_id": user})

        if query is None:
            return query
        return User(**query)

    def get_user_db(self, username: str | ObjectId) -> User_DB:
        """Method that returns all user info from database by username or id

        Args:
            username (str | ObjectId): username or user id

        Returns:
            User_DB: user data, including hashed password and update statuses
        """

        if type(username) is str:
            query = self.db.users.find_one({"username": username})
        if type(username) is ObjectId:
            query = self.db.users.find_one({"_id": username})

        if query is None:
            return query

        return User_DB(**query)

    def get_user_id(self, username: str) -> ObjectId:

        query = self.db.users.find_one({"username": username})
        if query is None:
            return query
        return query["_id"]

    def search_users(self, username: str) -> list[User]:
        """Method that searches the database for users that
        somewhat match the username"

        Args:
            username (str): User username

        Returns:
            list[User]: list of results
        """

        # query for name, case insensitive
        query = self.db.users.find(
            {"username": {"$regex": username, "$options": "i"}},
            {"username": 1, "_id": 0},
        )

        return query

    def post_user(self, user_data: User_DB) -> list[bool, ObjectId]:
        """Method that creates a user in the database

        Args:
            user_data (User_DB): user data with hashed password

        Returns:
            Union[bool, ObjectId]: return code and the id of the newly inserted user
        """

        request = self.db.users.insert_one(user_data.model_dump())

        if request.acknowledged is False:
            return False, None

        return True, request.inserted_id

    def update_user(
        self,
        user_data: User,
        username: str,
    ) -> bool:
        """Method that updates user data

        Args:
            user_data (User): updated user data
            username (str): username of user to update

        Returns:
            bool: return code
        """

        request = self.db.users.update_one(
            {"username": username}, {"$set": user_data.model_dump()}
        )

        return request.acknowledged

    def delete_user(self, username: str) -> bool:
        """Delete user from the database

        Args:
            username (str): username of the user to delete

        Returns:
            bool: return code
        """
        request = self.db.users.delete_one({"username": username})

        return request.acknowledged

    def make_admin(self, username: str) -> bool:
        """Make a user an admin

        Args:
            username (str): username of user to be made admin

        Returns:
            bool: return code
        """

        request = self.db.users.update_one(
            {"username": username}, {"$set": {"power": "admin"}}
        )

        return request.acknowledged

    # TOKEN METHODS
    def get_token(self, token_uuid: UUID) -> Token_DB:
        """Get token from database via UUID, needed when checking or deleting
        token

        Args:
            token_uuid (UUID): token UUID

        Returns:
            dict: Token_DB data
        """

        query = self.db.sessions.find_one({"token": str(token_uuid)})
        if query is None:
            return query
        return Token_DB(**query)

    def post_token(self, token: Token, user_id: ObjectId) -> bool:
        """Create session token, triggered when logging in

        Args:
            token (Token): token
            user_id (ObjectId): user's id in the database

        Returns:
            bool: return code
        """

        # convert Token to Token_DB
        token_db = token.convert(user_id)

        # insert Token_DB instance into database
        request = self.db.sessions.insert_one(token_db.model_dump())
        return request.acknowledged

    def get_token_by_user(self, user_id: ObjectId) -> Token:
        query = self.db.sessions.find_one({"user_id": user_id})

        if query is None:
            return query
        return Token(**query)

    def delete_token(self, token_uuid: UUID) -> bool:
        """Method that deletes session token if the user logs in again or if
        the token is expired

        Args:
            token_uuid (UUID): session token

        Returns:
            bool: return code
        """

        request = self.db.sessions.delete_one({"token": str(token_uuid)})

        return request.acknowledged

    # PROJECT METHODS
    def get_all_project(self, username: str) -> cursor:

        request = self.db.projects.find({"members": {"$elemMatch": {"$eq": username}}})

        return request

    def add_project(self, project: Project) -> bool:

        request = self.db.projects.insert_one(project.model_dump())

        return request.acknowledged

    def get_project(self, project_name: str) -> Project:

        request = self.db.projects.find_one({"name": project_name})
        if request is None:
            return request

        return Project(**request)

    def update_project(self, project_name: str, updated_project: Project) -> bool:

        request = self.db.projects.update_one(
            {"name": project_name}, {"$set": updated_project.model_dump()}
        )

        # update all members
        for username in updated_project.members:
            user_db = User_DB(**self.db.users.find_one({"username": username}))
            if updated_project.name not in user_db.update_projects:
                self.db.users.update_one(
                    {"username": username},
                    {"$push": {"update_projects": updated_project.name}},
                )

        return request.acknowledged

    def delete_project(self, project_name: str) -> bool:

        request = self.db.projects.delete_one({"name": project_name})

        return request.acknowledged
