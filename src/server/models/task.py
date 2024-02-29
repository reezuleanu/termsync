from __future__ import annotations
from pydantic import BaseModel
from typing import List
from .user import User


# "abstract" Task class
class Task(BaseModel):
    """Base class for Tasks, should not be used in itself, but rather inherited"""

    name: str
    description: str | None = None
    members: List[User] | None = []

    def __eq__(self, other: Task) -> bool:
        return self.name == other.name

    def add_member(self, *members: User) -> bool:
        """Add members to the task"""
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
        """Remove members from the task"""
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


# concrete Task classes
class Discrete_Task(Task):
    """Task class based around a single job, it can either be finished, or not"""

    completed: bool | None = False


class Milestone_Task(Task):
    """Task class based around milestone goals. Has completion percentage"""

    milestones: int | None = 0
    completed: int | None = 0

    @property
    def percentage_completed(self) -> int:
        """Calculate percentage of completion

        Returns:
            int: percentage represented as an integer
        """

        return int((self.completed / self.milestones) * 100)
