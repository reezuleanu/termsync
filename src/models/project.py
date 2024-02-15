from pydantic import BaseModel
from typing import List
from .task import Task
from .user import User


class Project(BaseModel):
    id: str | None = None
    name: str
    description: str | None = None
    tasks: List[Task] | None = []
    members: List[User] | None = []

    # task related methods

    def add_task(self, task: Task) -> bool:
        """Add a single task to the project (could get messy if I tried to accomodate for multiple tasks at once, so I will do it like this for now)"""

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

    def add_member(self, *members: User) -> bool:
        """Add members to the project"""
        duplicates: bool = False
        for member in members:
            if member in self.members:
                duplicates = True
                continue
            self.members.append(member)
        # if everything went well, return true. if some users could not be added, return false
        if duplicates:
            return False
        return True

    def remove_member(self, *members: User) -> bool:
        """Remove members from the project"""
        not_found: bool = False
        for member in members:
            if member not in self.members:
                not_found = True
                continue
            self.members.remove(member)
        # if everything went well, return true. if some users could not be removed, return false
        if not_found:
            return False
        return True
