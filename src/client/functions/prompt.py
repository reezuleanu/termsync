from rich.console import Console
from rich.text import Text
import httpx
import time
from .user_functions import login, register, test
from .help import help
from utils import clear_screen

# available commands
commands = {
    "login": login,
    "register": register,
    "clear": clear_screen,
    "test": test,
    "help": help,
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

            self.parent.console.print(
                f"[{time.strftime('%H:%M:%S', time.localtime())}]", end=""
            )
            command = input(f"[{username}] >> ")
            self.parent.console.print()

            # split command by spaces
            command = command.split(" ")

            # apply command with arguments
            if command[0] in commands:
                try:
                    if command[0] == "login" or command[0] == "register":
                        username = commands[command[0]](*command[1::])
                        self.run(username)
                    else:
                        commands[command[0]](*command[1::])
                        self.run(username)

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

            # TODO figure out how to break out of prompt loop and restart startup
            elif command[0] == "disconnect":
                with open("data/session.json", "w") as fp:
                    fp.write("")
                self.parent.console.print(
                    "You have disconnected successfully\n", style="success"
                )
                # self.run(None)
                self.parent.startup()
            else:
                self.parent.console.print("Bad command\n", style="danger")
