from __future__ import annotations
from pydantic import BaseModel
from uuid import uuid4, uuid5, UUID
from datetime import datetime, timedelta


class Token(BaseModel):
    """Session Token dataclass"""

    # could not use UUID type because mongodb has trouble converting it to bson
    token: UUID
    # time when token expires (72 hours from creation)
    expiration: datetime

    @classmethod
    def generate(cls, username: str) -> Token:
        """Class method for generating a token

        Returns:
            Token: generated token
        """
        # using uuid5 to avoid the astronomical chance of duplicate UUIDs
        namespace = uuid4()
        # token = str(uuid5(namespace=namespace, name=username))
        token = uuid5(namespace=namespace, name=username)

        # calculate time when token expires
        lifetime = timedelta(hours=72)
        expiration = datetime.now() + lifetime

        # return token
        return cls(token=token, expiration=expiration)

    def check_alive(self) -> bool:
        """Method which checks if the token has expired already"""

        # current time
        now = datetime.now()

        # a timedelta object with no time in it, equivalent to 0
        null_time = timedelta()

        return self.expiration - now > null_time

    def convert(self, user_id: str) -> Token_DB:
        """Method to convert the Token class to Token_DB, a class better suited for database storage

        Returns:
            Token_DB: converted token
        """
        data = self.model_dump()
        data["token"] = str(self.token)
        return Token_DB(user_id=user_id, **data)


class Token_DB(Token):
    user_id: str
    token: str
