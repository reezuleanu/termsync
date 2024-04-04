from uuid import UUID
import httpx
from models import User
import hashlib

from utils import NotAdmin

# import yaml


class API:
    """API interface component"""

    def __init__(self, host, port) -> None:
        self.host = host
        self.port = port
        self.server = f"http://{host}:{port}"
        self.client = httpx.Client(base_url=self.server)

    # USER METHODS

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
        """Method that checks if the token is still valid

        Args:
            token (UUID): session token

        Returns:
            bool: token validity
        """

        response = self.client.get(
            "/",
            headers={"content-type": "application/json", "token-uuid": token},
        )
        if response.status_code == 200:
            return True
        else:
            return False

    # ! UNUSED
    def check_admin(self, token: UUID) -> bool:
        """Check if user is admin

        Args:
            token (UUID): session token

        Returns:
            bool: is admin
        """

        response = self.client.get(
            "/",
            headers={"content-type": "application/json", "token-uuid": token},
        )

        if response.status_code != 200:
            return None
        return response.json()["admin"]

    def post_user(self, user: User, password: str) -> UUID:
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
        """Get user data from api

        Args:
            token (str): session token
            username (str): username of user to get data of

        Returns:
            User: user data
        """

        response = self.client.get(
            f"/users/{username}",
            headers={"content-type": "application/json", "token-uuid": token},
        )

        if response.status_code == 200:
            return User(**response.json())
        else:
            return None

    def delete_user(self, token: str, username: str, password: str) -> int:
        """Delete user

        Args:
            token (str): session token
            username (str): username of user to delete
            password (str): user password for confirmation

        Raises:
            NotAdmin: if trying to delete another account and you are not an admin

        Returns:
            int: return code
        """

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

    def put_user(self, token: str, user_data: User) -> int:

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
        """Make user admin. Must be an admin yourself

        Args:
            token (str): session token
            username (str): username of user to promote

        Raises:
            NotAdmin: if not admin

        Returns:
            int: return code
        """

        response = self.client.post(f"/admin/{username}", headers={"token-uuid": token})

        if response.status_code == 200:
            return 0
        elif response.status_code == 401:
            raise NotAdmin
        elif response.status_code == 404:
            return 2
        else:
            return 1

    # PROJECT METHODS

    def post_project() -> int:
        raise NotImplementedError

    def get_project() -> int:
        raise NotImplementedError

    def put_project() -> int:
        raise NotImplementedError

    def delete_project() -> int:
        raise NotImplementedError


# with open("data/settings.yaml", "r") as fp:
#     host = yaml.load(fp, )


# object used throughout the app
api = API("127.0.0.1", 2727)
