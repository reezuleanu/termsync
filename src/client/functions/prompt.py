from rich.console import Console
from rich.text import Text
import httpx
import time
from .user_functions import (
    login,
    register,
    test,
    get_user,
    make_admin,
    account,
)
from .help import help
from utils import clear_screen, get_username, NotLoggedIn

# available commands
commands = {
    "login": login,
    "register": register,
    "clear": clear_screen,
    "test": test,
    "help": help,
    "account": account,
    "user": get_user,
    "op": make_admin,
}


class Prompt:
    def __init__(self, parent) -> None:
        self.parent = parent

    def run(self, username: str) -> None:
        """Function that takes user commands (with arguments) and executes them

        Args:
            console (Console): Rich console
            username (str): user's username (displayed in the prompt)
        """

        while True:

            timestamp = time.strftime("%H:%M:%S", time.localtime())
            self.parent.console.print(f"[{timestamp}]", end="")
            command = input(f"[{username}] >> ")
            self.parent.console.print()

            # split command by spaces
            command = command.split(" ")

            # apply command with arguments
            if command[0] in commands:
                try:
                    commands[command[0]](*command[1::])
                    self.run(get_username())

                except NotLoggedIn:
                    self.parent.startup()

                except httpx.ConnectError:
                    self.parent.console.print(
                        "\nCannot connect to server\n", style="danger"
                    )
                except AttributeError:
                    self.parent.console.print(
                        f"\nIncorrect usage, please use 'help {command[0]}' for instructions.\n",
                        style="warning",
                    )

            elif command[0] == "":
                print()
            elif command[0] == "exit":
                raise KeyboardInterrupt
            elif command[0] == "restart":
                self.parent.startup()

            elif command[0] == "disconnect":
                with open("data/session.json", "w") as fp:
                    fp.write("")
                self.parent.console.print(
                    "You have disconnected successfully\n", style="success"
                )
                self.run(None)
            else:
                self.parent.console.print("Bad command\n", style="danger")
