import shutil
import httpx
import time
from .user_functions import (
    login,
    register,
    make_admin,
    user,
)
from .project_functions import project

from .help import help
from utils import clear_screen, get_username, NotLoggedIn

# available commands
commands = {
    "login": login,
    "register": register,
    "clear": clear_screen,
    "help": help,
    "account": user,
    "user": user,
    "op": make_admin,
    "project": project,
}


class Prompt:
    """App prompt component"""

    def __init__(self, parent) -> None:
        self.parent = parent

    def run(self, username: str) -> None:
        """Function that takes user commands (with arguments) and executes them

        Args:
            console (Console): Rich console
            username (str): user's username (displayed in the prompt)
        """

        while True:

            terminal_width, _ = shutil.get_terminal_size()

            # prompt
            timestamp = time.strftime("%H:%M:%S", time.localtime())

            # use ansi escape codes to align the status and the prompt on the same line
            print(
                f"\033[{terminal_width - len(self.parent.status.value)}G", end=""
            )  # set cursor to end of line - status length

            self.parent.console.print(
                f"[{self.parent.status.value}]",
                end="\r",
            )  # print status, end at the beginning of the line

            self.parent.console.print(
                f"[{timestamp}]", end=""
            )  # print timestamp, keep cursor on the same line

            # input
            command = input(f"[{username}] >> ")  # print prompt

            self.parent.console.print()  # add space

            # split command by spaces
            command = command.split(" ")

            # apply command with arguments
            if command[0] in commands:
                try:
                    commands[command[0]](*command[1::])
                    self.run(get_username())

                except NotLoggedIn:
                    self.parent.startup()  # restart app

                except (httpx.ConnectError, httpx.ReadTimeout):
                    self.parent.console.print(
                        "Cannot connect to server\n", style="danger"
                    )
                except (AttributeError, TypeError):
                    self.parent.console.print(
                        f"Incorrect usage, please use 'help {command[0]}' for instructions.\n",
                        style="warning",
                    )
                except NotImplementedError:
                    self.parent.console.print(
                        "This feature is not yet finished, please be patient\n",
                        style="warning",
                    )

            elif command[0] == "":
                continue
            elif command[0] == "exit":
                raise KeyboardInterrupt
            elif command[0] == "restart":
                self.parent.startup()  # restart app

            elif command[0] == "disconnect":
                # wipe session data
                with open("data/session.json", "w") as fp:
                    fp.write("")
                self.parent.console.print(
                    "You have disconnected successfully\n", style="success"
                )
                self.run(None)
            else:
                self.parent.console.print("Bad command\n", style="danger")
