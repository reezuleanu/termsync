from __future__ import annotations
from pydantic import BaseModel
from uuid import uuid4, uuid5, UUID
from datetime import datetime, timedelta


class Token(BaseModel):
    """Session Token dataclass"""

    token: UUID

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

        # return token
        return cls(token=token)

    def convert(self, user_id: str) -> Token_DB:
        """Method to convert the Token class to Token_DB, a class better
        suited for database storage

        Returns:
            Token_DB: converted token
        """

        data = self.model_dump()
        data["token"] = str(self.token)

        # calculate time when token expires
        lifetime = timedelta(hours=72)
        expiration = datetime.now() + lifetime

        # return token
        return Token_DB(user_id=user_id, expiration=expiration, **data)


class Token_DB(Token):

    # this is a string here because mongodb can't serialize it properly or
    # something
    user_id: str
    token: str
    authorization: str | None = "user"

    # time when token expires (72 hours from creation)
    expiration: datetime

    def check_alive(self) -> bool:
        """Method which checks if the token is still valid"""

        # current time
        now = datetime.now()

        # removing timezone info
        now = now.replace(tzinfo=None)
        self.expiration = self.expiration.replace(tzinfo=None)

        # a timedelta object with no time in it, equivalent to 0
        null_time = timedelta()

        return self.expiration - now > null_time
