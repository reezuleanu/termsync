# global imports
from pymongo import MongoClient


# def authorize_token(token: Token, auth_level: str | None = "user") -> bool | Token:
#     """Function which checks if the provided token is valid, and if
#     the user has the required authorization for the API call

#     Args:
#         token (Token): token from request header
#         auth_level (str): authorization level required ("user", "admin", etc.)

#     Returns:
#         bool: if the token is invalid / the user doesn't have sufficient permissions
#         Token: if everything is alright
#     """
#     # check if token in database
#     token_data = token.model_dump()
#     token_data["token"] = str(token_data["token"])

#     query = db.sessions.find_one(token_data)

#     if query is None:
#         return False

#     # check if the token is not expired
#     token_db_data = bson2dict(query)

#     # convert whatever the hell mongodb stores (i am already sick of its
#     # typing bullshit) to a datetime object
#     token_db_data["expiration"] = datetime.fromisoformat(
#         token_db_data["expiration"]["$date"]
#     )

#     token_db = Token_DB(**token_db_data)
#     if not token_db.check_alive():
#         return False

#     # check auth level
#     if token_db.authorization != auth_level:
#         return False

#     return token_db


DB_HOST = "127.0.0.1"
DB_PORT = 27017


# TODO implement database methods
class Database:
    """Pymongo database interface class"""

    def __init__(self) -> None:
        self.client = MongoClient(host=DB_HOST, port=DB_PORT)
        self.db = self.client.tests

    def add(self, object_data: object) -> bool:
        """Add object to database

        Returns:
            bool: return code
        """
        raise NotImplementedError

    def get(self, object_id: str) -> object:
        raise NotImplementedError

    def update(self, oject_id: str, object_data: object) -> bool:
        raise NotImplementedError

    def delete(self, object_id: str) -> bool:
        raise NotImplementedError
