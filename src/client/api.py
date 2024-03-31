from uuid import UUID
import httpx


class API:
    """API interface"""

    def __init__(self, host, port) -> None:
        self.host = host
        self.port = port
        self.server = f"http://{host}:{port}"
        self.client = httpx.Client()

    def check_token(self, token: UUID) -> bool:
        """Method that checks if the token is still valid"""

        response = self.client.get(
            f"{self.server}/",
            headers={"content-type": "application/json", "token-uuid": token},
        )
        if response.status_code == 200:
            return True
        else:
            return False

    def login(self, username: str, password: str) -> UUID:
        """Method that logs user in

        Args:
            username (str): user username
            password (str): user hashed password

        Returns:
            UUID: token uuid
        """

        response = self.client.post(
            f"{self.server}/login/", json={"username": username, "password": password}
        )

        if response.status_code == 200:
            return response.json()["token"]
        else:
            return None
