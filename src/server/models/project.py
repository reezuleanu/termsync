from pydantic import BaseModel, WithJsonSchema
from typing import List, Annotated, Union
from bson import ObjectId

from .task import Task, Milestone_Task, Discrete_Task
from .user import User
from ..utils import replace

# ! Circular import, used only for type hinting
# from ..database import Database


class Project(BaseModel):

    # owner_id: Annotated[Union[ObjectId | None], WithJsonSchema({"type": "string"})] = (
    #     None  # id of user who created project
    # )

    owner: str | None = None  # username of user who created project

    # moderators: Annotated[
    #     Union[List[ObjectId] | None], WithJsonSchema({"type": "string"})
    # ] = []  # list of people allowed to modify things

    moderators: List[str] | None = []  # list of people allowed to modify things

    name: str  # unique
    description: str | None = None
    tasks: List[Milestone_Task | Discrete_Task] | None = []

    # members: List[ObjectId | str] | None = []  # user id or username

    members: List[str] | None = []  # usernames of members

    # allow ObjectId
    model_config = {"arbitrary_types_allowed": True}

    # task related methods
    def add_task(self, task: Task) -> bool:
        """Add a single task to the project (could get messy if I tried to
        accomodate for multiple tasks at once, so I will do it like this for
        now)"""

        # check if there is a task with that name already, then add it
        if task in self.tasks:
            return False
        else:
            self.tasks.append(task)
            return True

    def remove_task(self, *tasks: Task) -> bool:
        """Remove one or more tasks from the project

        Args:
            task_names (Task): task(s) to be deleted

        Returns:
            bool: True = success, False = something happened
        """
        not_found: bool = False
        for task in tasks:
            for existing_task in self.tasks:
                if task == existing_task:
                    self.tasks.remove(task)
                    continue
                not_found = True
        if not_found:
            return False
        return True

    # member related methods
    def add_member(self, *member_names: str) -> bool:
        """Add members to the project"""

        duplicates: bool = False
        for member in member_names:
            if member in self.members:
                duplicates = True
                continue
            self.members.append(member)
        # if everything went well, return true. if some users could not be
        # added, return false
        if duplicates:
            return False
        return True

    def remove_member(self, *member_names: str) -> bool:
        """Remove members from the project"""

        not_found: bool = False
        for member in member_names:
            if member not in self.members:
                not_found = True
                continue
            self.members.remove(member)
        # if everything went well, return true. if some users could not be
        # removed, return false
        if not_found:
            return False
        return True

    # moderator methods
    def add_moderator(self, *moderator_names: str) -> bool:
        """Add user(s) as moderator(s) by username

        Returns:
            bool: return code
        """

        duplicate: bool = False
        for moderator in moderator_names:
            # if the moderator we are trying to add already is a moderator, skip over it
            if moderator in self.moderators:
                duplicate = True
                continue
            self.moderators.append(moderator)

        # if there was a duplicate, return false to show something happened
        if duplicate:
            return False

        return True

    def remove_moderator(self, *moderator_names: str) -> bool:
        """Remove user(s) from being a moderator

        Returns:
            bool: return code
        """

        not_found: bool = False
        for moderator in moderator_names:
            if moderator not in self.moderators:
                not_found = True
                continue
            self.moderators.remove(moderator)
        # if everything went well, return true. if some users could not be
        # removed, return false
        if not_found:
            return False

        return True

    # ! DEPRECATED
    def render(self, db) -> None:
        """Convert all ObjectIds to usernames before sending to Client"""

        # convert members
        for member_id in self.members:
            member_username = db.get_user(member_id).username

            # if the user is not found in the database, remove it from the list
            if member_id is None:
                self.members.remove(member_id)
                continue
            replace(self.members, member_id, member_username)

        # convert owner id to username
        self.owner_id = db.get_user(self.owner_id).username

    # ! DEPRECATED
    def convert(self, db) -> None:
        """Convert all usernames to ObjectIds before sending to Database"""

        # convert owner
        for member_username in self.members:
            member_id = db.get_user_id(member_username)

            # if the user is not found in the database, remove it from the list
            if member_username is None:
                self.members.remove(member_username)
                continue
            replace(self.members, member_username, member_id)

        # convert owner username to id
        self.owner_id = db.get_user_id(self.owner_id)
