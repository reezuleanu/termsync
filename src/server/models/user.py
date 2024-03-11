from __future__ import annotations
from pydantic import BaseModel


class User(BaseModel):
    """Dataclass containing user data. (DB hold a subclass of this with the password as well)"""

    username: str
    full_name: str

    # the username will be unique across all users
    def __eq__(self, other: User) -> bool:
        return self.username == other.username


class User_DB(User):
    """Dataclass containing user data AND HASHED PASSWORD. Not to be transmitted"""

    password: str  # hashed password

    power: str = "user"  # user administrator priviledges (user/admin)

    # todo redo updating system
    # attribute telling the client should refresh projects
    update: bool = False
