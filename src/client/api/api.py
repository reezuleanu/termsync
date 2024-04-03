from uuid import UUID
import httpx
from models import User
import hashlib

from utils import NotAdmin

# import yaml


class API:
    """API interface"""

    def __init__(self, host, port) -> None:
        self.host = host
        self.port = port
        self.server = f"http://{host}:{port}"
        self.client = httpx.Client(base_url=self.server)

    def get_username(self, token: UUID) -> str:
        """Get user's username to display in prompt"""

        response = self.client.get(
            "/",
            headers={"content-type": "application/json", "token-uuid": token},
        )

        if response.status_code != 200:
            return None
        return response.json()["username"]

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

    def check_admin(self, token: UUID) -> bool:

        response = self.client.get(
            "/",
            headers={"content-type": "application/json", "token-uuid": token},
        )

        if response.status_code != 200:
            return None
        return response.json()["admin"]

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

    def get_user(self, token: str, username: str) -> User:

        response = self.client.get(
            f"/users/{username}",
            headers={"content-type": "application/json", "token-uuid": token},
        )

        if response.status_code == 200:
            return User(**response.json())
        else:
            return None

    def delete_user(self, token: str, username: str, password: str) -> int:

        # hash password
        password = password.encode("utf-8")
        password = hashlib.sha256(password).hexdigest()

        response = self.client.request(
            "DELETE",
            f"/users/{username}",
            headers={"content-type": "application/json", "token-uuid": token},
            json=password,
        )
        if response.status_code == 200:
            return 0
        elif response.status_code == 401:
            raise NotAdmin
        else:
            return 1

    def edit_user(self, token: str, user_data: User) -> int:

        response = self.client.put(
            f"/users/{user_data.username}",
            headers={"content-type": "application/json", "token-uuid": token},
            json=user_data.model_dump(),
        )

        if response.status_code == 200:
            return 0
        elif response.status_code == 401:
            raise NotAdmin
        else:
            return 1

    def make_admin(self, token: str, username: str) -> int:

        response = self.client.post(f"/admin/{username}", headers={"token-uuid": token})

        if response.status_code == 200:
            return 0
        elif response.status_code == 401:
            raise NotAdmin
        elif response.status_code == 404:
            return 2
        else:
            return 1


# with open("data/settings.yaml", "r") as fp:
#     host = yaml.load(fp, )


# object used throughout the app
api = API("127.0.0.1", 2727)
