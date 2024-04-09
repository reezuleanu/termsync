from rich.console import Console
from time import sleep
from enum import Enum
from sys import exit

from api import API
from ui import display_logo
from utils import (
    clear_screen,
    get_token,
    get_username,
    write_update_cache,
    read_update_cache,
)
from functions import Prompt


class Status(Enum):
    CONNECTED = "[green]connected[/]"
    DISCONNECTED = "[red]disconnected[/]"
    UPDATE = "🔔[yellow]update[/]"


class State(Enum):
    RUNNING = "running"
    EXITING = "exiting"


class App:
    """Class for the app proper"""

    def __init__(self, console: Console, api: API) -> None:
        self.console = console  # rich console
        self.api = api  # api interface
        self.prompt = Prompt(parent=self)  # prompt component
        self.status = Status.DISCONNECTED  # connection status
        self.state = State.RUNNING  # app status

    def startup(self) -> None:
        """App startup function. It displays logo, checks token, then passes control to the prompt function

        Args:
            console (Console): Rich console
        """

        clear_screen()

        # display logo
        display_logo(self.console)
        self.console.print("\n\n")  # add a bit of space

        # get token from session.json
        token = get_token()

        if token is None:
            self.console.print(
                "You are not logged in. To use the app, please use 'login' to login with an existing account, or 'register' to create a new account\n",
                style="warning",
            )
            self.prompt.run(None)
        else:
            # check if the token is still valid
            rc = None
            i = 0
            # status with spinner
            with self.console.status(
                "[bold red]Retrying[/]",
                spinner="simpleDotsScrolling",
                spinner_style="bold white",
            ):
                while rc is None and i < 5:
                    try:
                        rc = self.api.check_token(token)
                    # in case of connection issues
                    except:
                        i = i + 1
                        self.console.print(
                            "Could not connect to server\n",
                            style="danger",
                        )
                        # self.console.print("Retrying...\n")
                        sleep(5)

            # if failed to connect to server and check token
            if rc is None:
                self.console.print(
                    "Could not connect to the server, please try again later\n",
                    style="danger",
                )
                self.prompt.run(None)

            # if it got to this point, it means it connected to the server
            self.status = Status.CONNECTED

            # if token is expired
            if rc is False:
                self.console.print(
                    "Session has expired, please login again to use the app\n",
                    style="warning",
                )
                self.prompt.run(None)

            # if token is still valid
            if rc is True:
                self.console.print("You are logged in\n", style="success")
                self.prompt.run(get_username())

    def run(self) -> None:
        try:
            while True:
                self.startup()

        # shutdown sequence
        except KeyboardInterrupt:
            self.state = State.EXITING
            self.api.client.close()
            clear_screen()
            exit(0)

    def get_update(self) -> None:
        """Thread that periodically checks in with the api. It determines if the client is still connected,
        and handles the project update functionality"""

        while self.state == State.RUNNING:
            token = get_token()

            try:
                response = self.api.get_project_updates(token)

                if response.status_code == 200:

                    if len(response.json()) > 0 or read_update_cache() != [""]:
                        self.status = Status.UPDATE

                        if len(response.json()) > 0:
                            write_update_cache(*response.json())
                    else:
                        self.status = Status.CONNECTED
                else:
                    self.status = Status.DISCONNECTED

                sleep(3)
            except:
                self.status = Status.DISCONNECTED
                continue
