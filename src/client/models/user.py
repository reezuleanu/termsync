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
