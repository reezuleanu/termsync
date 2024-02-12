from pydantic import BaseModel


class User(BaseModel):
    """Dataclass containing user data. (DB hold a subclass of this with the password as well)"""

    id: str | None = None  # will be provided by the database upon successful completion
    username: str
    full_name: str


class User_DB(User):
    """Dataclass containing user data AND HASHED PASSWORD. Not to be transmitted"""

    password: str
    update: bool = False
