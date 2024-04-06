from rich.console import Console
from time import sleep

from api import API
from ui import display_logo
from utils import clear_screen, get_token, get_username
from functions import Prompt


class App:

    def __init__(self, console: Console, api: API) -> None:
        self.console = console
        self.api = api
        self.prompt = Prompt(parent=self)

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
            while rc is None and i < 5:
                try:
                    rc = self.api.check_token(token)
                except:
                    i = i + 1
                    self.console.print(
                        "Could not connect to server\n",
                        style="danger",
                    )
                    self.console.print("Retrying...\n")
                    sleep(5)

            # if failed to connect to server and check token
            if rc is None:
                self.console.print(
                    "Could not connect to the server, please try again later\n",
                    style="danger",
                )
                self.prompt.run(None)

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
            # logo print
            # display_logo(console)
            # display_logo(console)
            # display_logo(console)

            # ! Layout example
            # layout = Layout()
            # panel_left = Panel.fit(
            #     # "This is not a warning",
            #     logo2,
            #     border_style="blue",
            # )
            # panel_center = Panel.fit(
            #     # "This is not a warning",
            #     logo2,
            #     border_style="blue",
            # )
            # layout.split_row(Layout(name="left"), Layout(name="center"))
            # layout["left"].update(panel_left)
            # layout["center"].update(panel_center)
            # layout["right"].update(Panel.fit(logo, border_style="red", style="bold red"))
            # console.print(layout)

            while True:
                self.startup()
        except KeyboardInterrupt:
            self.api.client.close()
            clear_screen()
