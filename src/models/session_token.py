from __future__ import annotations
from pydantic import BaseModel


class Token(BaseModel):
    """Session Token dataclass"""

    token: str

    @classmethod
    def generate(cls) -> Token:
        """Class method for generating a token

        Returns:
            Token: generated token
        """

        # TODO implement token generation algoritm
        token = "213"
        return cls(token=token)
