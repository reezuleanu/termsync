from uuid import UUID
import httpx
from httpx import Response
from models import User, Project, Discrete_Task, Milestone_Task
import hashlib

from utils import NotAdmin, get_settings


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

        # api call
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

        # api call
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

    def get_multiple_users(self, token: str, username: str) -> list[str]:
        """Query the server for all users with a similar username

        Args:
            username (str): username to query by

        Returns:
            list[str]: search results
        """
        response = self.client.get(
            f"/users/?search={username}", headers={"token-uuid": token}
        )

        if response.status_code == 200:
            return response.json()
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

        # api call
        response = self.client.request(
            "DELETE",
            f"/users/{username}",
            headers={"content-type": "application/json", "token-uuid": token},
            json=password,
        )

        # tried using return codes for a while
        if response.status_code == 200:
            return 0
        elif response.status_code == 401:
            raise NotAdmin
        elif response.status_code == 404:
            return 2
        else:
            return 1

    def put_user(self, token: str, user_data: User) -> int:
        """Update user data

        Args:
            token (str): session token
            user_data (User): new user data

        Raises:
            NotAdmin: if you try to edit another user's data without being an admin

        Returns:
            int: return code
        """

        # api call
        response = self.client.put(
            f"/users/{user_data.username}",
            headers={"content-type": "application/json", "token-uuid": token},
            json=user_data.model_dump(),
        )

        # return codes
        if response.status_code == 200:
            return 0
        elif response.status_code == 401:
            raise NotAdmin
        elif response.status_code == 404:
            return 2
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

    def post_project(self, project_data: Project, token: str) -> int:
        """Create project

        Args:
            project_data (Project): project data
            token (str): session token

        Returns:
            int: return code
        """

        # api call
        response = self.client.post(
            "/projects/",
            headers={"content-type": "application/json", "token-uuid": token},
            json=project_data.model_dump(),
        )

        # if successful
        if response.status_code == 200:
            return 0

        # if name already taken
        if response.status_code == 403:
            return 2

        # if any other error
        else:
            return 1

    def get_project(self, token: str, project_name: str) -> Project:
        """Get project data from API

        Args:
            token (str): session token
            project_name (str): name of project

        Returns:
            Project: project data
        """

        response = self.client.get(
            f"/projects/{project_name}",
            headers={"content-type": "application/json", "token-uuid": token},
        )

        if response.status_code == 200:
            return Project(**response.json())
        else:
            return response.status_code

    def get_all_projects(self, token: str) -> dict:
        """Get all projects the user is a member of

        Args:
            token (str): session token

        Returns:
            dict: results in format project_name: project_progress
        """

        response = self.client.get("/projects/all/", headers={"token-uuid": token})

        if response.status_code == 200:
            return response.json()
        else:
            return response.status_code

    def put_project(self, token: str, project_name: str, updated_data: Project) -> int:
        """Update project data

        Args:
            token (str): session token
            project_name (str): name of project to update
            updated_data (Project): updated data

        Raises:
            NotAdmin: if trying to modify a project you are not a user of, without being an admin

        Returns:
            int: http status code
        """

        response = self.client.put(
            f"/projects/{project_name}",
            headers={"content-type": "application/json", "token-uuid": token},
            json=updated_data.model_dump(),
        )

        # started using the HTTP status code as an rc
        if response.status_code == 403:
            raise NotAdmin
        return response.status_code

    def delete_project(self, token: str, project_name: str) -> int:
        """Delete project from server

        Args:
            token (str): session token
            project_name (str): name of project to delete

        Raises:
            NotAdmin: if trying to delete a project you are not the owner of, without being an admin

        Returns:
            int: http status code
        """

        response = self.client.delete(
            f"/projects/{project_name}", headers={"token-uuid": token}
        )

        if response.status_code == 403:
            raise NotAdmin
        return response.status_code

    def project_add_member(self, token: str, project_name: str, username: str) -> int:
        """Add a member to an existing project

        Args:
            token (str): session token
            project_name (str): name of project to add a member to
            username (str): member's username

        Raises:
            NotAdmin: if not owner/moderator/admin

        Returns:
            int: http status code
        """

        response = self.client.post(
            f"/projects/{project_name}/members/{username}",
            headers={"token-uuid": token},
        )

        if response.status_code == 403:
            raise NotAdmin
        return response.status_code

    def project_remove_member(
        self, token: str, project_name: str, username: str
    ) -> int:
        """Remove member from project

        Args:
            token (str): session token
            project_name (str): name of project to remove member from
            username (str): member's username

        Raises:
            NotAdmin: if not owner/moderator/admin

        Returns:
            int: http status code
        """

        response = self.client.delete(
            f"/projects/{project_name}/members/{username}",
            headers={"token-uuid": token},
        )

        if response.status_code == 403:
            raise NotAdmin
        return response.status_code

    def project_add_moderator(
        self, token: str, project_name: str, username: str
    ) -> int:
        """Promote a project member to moderator

        Args:
            token (str): session token
            project_name (str): project name
            username (str): username of member to promote

        Raises:
            NotAdmin: if not owner/admin

        Returns:
            int: http status code
        """

        response = self.client.post(
            f"/projects/{project_name}/moderators/{username}",
            headers={"token-uuid": token},
        )

        if response.status_code == 403:
            raise NotAdmin
        return response.status_code

    def project_remove_moderator(
        self, token: str, project_name: str, username: str
    ) -> int:
        """Demote member from moderator

        Args:
            token (str): session token
            project_name (str): project name
            username (str): username of member to demote

        Raises:
            NotAdmin: if not owner/admin

        Returns:
            int: http status code
        """
        response = self.client.delete(
            f"/projects/{project_name}/moderators/{username}",
            headers={"token-uuid": token},
        )

        if response.status_code == 403:
            raise NotAdmin
        return response.status_code

    def project_post_task(
        self, token: str, project_name: str, task_data: Discrete_Task | Milestone_Task
    ) -> int:
        """Add task to project

        Args:
            token (str): session token
            project_name (str): project name
            task_data (Discrete_Task | Milestone_Task): task data

        Raises:
            NotAdmin: if not owner/moderator/admin

        Returns:
            int: http status code
        """

        response = self.client.post(
            f"/projects/{project_name}/tasks/",
            headers={"token-uuid": token},
            json=task_data.model_dump(),
        )

        if response.status_code == 403:
            raise NotAdmin
        return response.status_code

    def project_put_task(
        self,
        token: str,
        project_name: str,
        task_name: str,
        updated_data: Discrete_Task | Milestone_Task,
    ) -> int:
        """Update task within project

        Args:
            token (str): session token
            project_name (str): project name
            task_name (str): name of task to update
            updated_data (Discrete_Task | Milestone_Task): new task data

        Raises:
            NotAdmin: if not owner/moderator/admin

        Returns:
            int: http status code
        """

        response = self.client.put(
            f"/projects/{project_name}/tasks/{task_name}",
            headers={"token-uuid": token},
            json=updated_data.model_dump(),
        )

        if response.status_code == 403:
            raise NotAdmin
        return response.status_code

    def project_delete_task(self, token: str, project_name: str, task_name: str) -> int:
        """Delete task from project

        Args:
            token (str): session token
            project_name (str): project name
            task_name (str): name of task to delete

        Raises:
            NotAdmin: if not owner/moderator/admin

        Returns:
            int: http status code
        """

        response = self.client.delete(
            f"/projects/{project_name}/tasks/{task_name}",
            headers={"token-uuid": token},
        )

        if response.status_code == 403:
            raise NotAdmin
        return response.status_code

    def project_task_post_member(
        self, token: str, project_name: str, task_name: str, username: str
    ) -> int:
        """Add members to task within project

        Args:
            token (str): session token
            project_name (str): project name
            task_name (str): task name
            username (str): username of member to add to task

        Raises:
            NotAdmin: if not owner/moderator/admin

        Returns:
            int: http status code
        """

        response = self.client.post(
            f"/projects/{project_name}/tasks/{task_name}/members/{username}",
            headers={"token-uuid": token},
        )
        if response.status_code == 403:
            raise NotAdmin
        return response.status_code

    def project_task_delete_member(
        self, token: str, project_name: str, task_name: str, username: str
    ) -> Response:
        """Delete member from task within project

        Args:
            token (str): session token
            project_name (str): project name
            task_name (str): task name
            username (str): username of member to remove from task

        Raises:
            NotAdmin: if not owner/moderator/admin

        Returns:
            Response: http response
        """

        response = self.client.delete(
            f"/projects/{project_name}/tasks/{task_name}/members/{username}",
            headers={"token-uuid": token},
        )

        # tried returning the whole http response to also use response detail in case of error
        # im still raising the custom exception since i already wrote it
        if response.status_code == 403:
            raise NotAdmin
        return response

    def project_task_update_progress(
        self, token: str, project_name: str, task_name: str, progress: int | bool
    ) -> Response:
        """Update progress of task within project

        Args:
            token (str): session token
            project_name (str): project name
            task_name (str): task name
            progress (int | bool): new task progress

        Raises:
            NotAdmin: if not owner/moderator/task member/admin

        Returns:
            Response: http response
        """

        response = self.client.put(
            f"/projects/{project_name}/tasks/{task_name}/completion?completion={progress}",
            headers={"token-uuid": token},
        )

        if response.status_code == 403:
            raise NotAdmin
        return response

    def get_project_updates(self, token: str) -> Response:
        """Get list of all projects that have been updated since last seen

        Args:
            token (str): session token

        Returns:
            Response: http response
        """

        response = self.client.get("/update/projects", headers={"token-uuid": token})

        return response


# get api settings
HOST = get_settings("HOST")
PORT = int(get_settings("PORT"))

# object used throughout the app
api = API(HOST, PORT)
