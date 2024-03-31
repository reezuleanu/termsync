from rich.console import Console
from ui import display_logo
from api import API
import json
import getpass

api = API(host="127.0.0.1", port=2727)


def startup(console: Console) -> None:
    """App startup function"""

    # display logo
    display_logo(console)

    with open("data/session.json", "r") as fp:
        try:
            token = json.load(fp)["token-uuid"]
        except json.decoder.JSONDecodeError:
            token = None

    if token is None:
        console.log("Please login")
        login(console)
    else:
        rc = api.check_token(token)

        if rc is False:
            console.log("Session has expired, please login again")
            login()
        if rc is True:
            console.log("You are logged in")


def login(console: Console) -> None:
    """Login functionality

    Args:
        console (Console): rich console
    """

    # input
    username = str(input("Username: "))
    password = str(getpass.getpass("Password: "))

    # login call
    token = api.login(username, password)

    # if call is not successfull
    if token is None:
        console.log("Wrong username or password")
        return

    # save token
    with open("data/session.json", "w") as fp:
        json.dump({"token-uuid": token}, fp)

    console.log("Login successful")
