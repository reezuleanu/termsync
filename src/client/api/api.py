from uuid import UUID
import httpx
from models import User
import hashlib


class API:
    """API interface"""

    def __init__(self, host, port) -> None:
        self.host = host
        self.port = port
        self.server = f"http://{host}:{port}"
        self.client = httpx.Client(base_url=self.server)

    def check_token(self, token: UUID) -> bool:
        """Method that checks if the token is still valid"""

        response = self.client.get(
            "/",
            headers={"content-type": "application/json", "token-uuid": token},
        )
        if response.status_code == 200:
            return True
        else:
            return False

    def register(self, user: User, password: str) -> UUID:
        """Method that registers a new user

        Args:
            user (User): user data
            password (str): hashed password

        Returns:
            UUID: token uuid
        """

        # hash password
        password = password.encode("utf-8")
        password = hashlib.sha256(password).hexdigest()

        response = self.client.post(
            "/users/",
            json={"user": user.model_dump(), "password": password},
        )

        if response.status_code == 200:
            return response.json()["token"]
        else:
            return None

    def login(self, username: str, password: str) -> UUID:
        """Method that logs user in

        Args:
            username (str): user username
            password (str): user hashed password

        Returns:
            UUID: token uuid
        """

        # hash password
        password = password.encode("utf-8")
        password = hashlib.sha256(password).hexdigest()

        response = self.client.post(
            "/login/", json={"username": username, "password": password}
        )

        if response.status_code == 200:
            return response.json()["token"]
        else:
            return None
