from rich.console import Console
from ui import display_logo
import json
from .prompt import prompt
from time import sleep
from api import api


def startup(console: Console) -> None:
    """App startup function. It displays logo, checks token, then passes control to the prompt function

    Args:
        console (Console): Rich console
    """

    # display logo
    display_logo(console)
    console.print("\n\n")  # add a bit of space

    # get token from session.json
    try:
        with open("data/session.json", "r") as fp:
            try:
                token = json.load(fp)["token-uuid"]
            except json.decoder.JSONDecodeError:
                token = None
    except FileNotFoundError:
        token = None

    if token is None:
        console.print(
            "You are not logged in. To use the app, please use 'login' to login with an existing account, or 'register' to create a new account\n",
            style="warning",
        )
        prompt(console, None)
    else:
        # check if the token is still valid
        rc = None
        i = 0
        while rc is None and i < 5:
            try:
                rc = api.check_token(token)
            except:
                i = i + 1
                console.print(
                    "Could not connect to server\n",
                    style="danger",
                )
                console.print("Retrying...\n")
                sleep(5)

        # if failed to connect to server and check token
        if rc is None:
            console.print(
                "Could not connect to the server, please try again later\n",
                style="danger",
            )
            prompt(console, None)

        # if token is expired
        if rc is False:
            console.print(
                "Session has expired, please login again to use the app\n",
                style="warning",
            )
            prompt(console, None)

        # if token is still valid
        if rc is True:
            console.print("You are logged in\n", style="success")
            prompt(console, api.get_username(token))
