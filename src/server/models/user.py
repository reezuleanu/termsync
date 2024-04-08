from __future__ import annotations
from pydantic import BaseModel
from bson import ObjectId
from typing import List


class User(BaseModel):
    """Dataclass containing user data. (DB hold a subclass of this with the password as well)"""

    model_config = {"arbitrary_types_allowed": True}

    username: str
    full_name: str
    profile_picture: str | None = None

    # the username will be unique across all users
    def __eq__(self, other: User) -> bool:
        return self.username == other.username


class User_DB(User):
    """Dataclass containing user data AND HASHED PASSWORD. Not to be transmitted"""

    password: str  # hashed password

    power: str = "user"  # user administrator priviledges (user/admin)

    # attribute telling the client if it should call GET for the IDs in the list
    update_projects: List[str] = []
    update_messages: List[str] = []
