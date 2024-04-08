from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from random import choice
import getpass
import json

from ui import console
from models import User
from api import API, api
from utils import get_token, get_username, NotLoggedIn, NotAdmin


def register(*args, console: Console = console, api: API = api) -> None:
    """Create new account functionality

    Args:
        console (Console, optional): Rich console. Defaults to console.
        api (API, optional): API interface. Defaults to api.
    """

    # gather data
    username = str(input("Enter username: "))
    full_name = str(input("\nEnter full name: "))
    password = str(getpass.getpass("\nEnter password: "))

    try:
        new_user = User(username=username, full_name=full_name)
    except:
        console.print("\nProvided details are not valid\n", style="danger")

    # api call and token serialization
    token = api.post_user(new_user, password)

    if token is None:
        console.print("\nCould not create new user", style="danger")
        return

    with open("data/session.json", "w") as fp:
        json.dump({"token-uuid": token, "username": username}, fp)

    console.print("\nUser created successfully\n", style="success")


def login(
    username: str | None = None, console: Console = console, api: API = api
) -> None:
    """Login functionality

    Args:
        username (str, optional): If username is provided with the command, the user will be asked only for the password. Defaults to None.
        console (Console, optional): Rich console. Defaults to console.
        api (API, optional): API interface. Defaults to api.
    """

    # input
    if username is None:
        username = str(input("Username: "))
        console.print()

    password = str(getpass.getpass("Password: "))

    # login call
    token = api.login(username, password)

    # if call is not successfull
    if token is None:
        console.print("\nWrong username or password\n", style="danger")
        username = None
    else:
        console.print("\nLogin successful\n", style="success")

    # save token (none if login failed)
    with open("data/session.json", "w") as fp:
        json.dump({"token-uuid": token, "username": username}, fp)


def delete_user(
    username: str | None = None,
    # token: str = get_token(),
    console: Console = console,
    api: API = api,
) -> None:
    """Delete account. Upon deletion, app exits

    Args:
        username (str | None, optional): Username of account to delete. If provided, it won't ask you for the username again.

    Raises:
        NotLoggedIn: invalid token
    """

    # check token
    token = get_token()
    if token is None or api.check_token(token) is False:
        raise NotLoggedIn

    # input
    if username is None:
        username = str(input("Username: "))

    password = str(getpass.getpass("\nPassword: "))

    # delete account api call
    try:
        rc = api.delete_user(token, username, password)
    except NotAdmin:
        console.print("\nYou cannot delete someone else's account\n", style="danger")
        return

    if rc == 1:
        console.print("\nCould not delete account\n", style="danger")
        return
    if rc == 2:
        console.print("\nCould not find user\n", style="danger")

    console.print("\nAccount deleted sucessfully\n", style="success")
    if username == get_username():
        console.print("Press Enter to exit\n")
        input()
        raise KeyboardInterrupt


def edit_user(
    username: str | None = None,
    # token: str = get_token(),
    console: Console = console,
    api: API = api,
) -> None:
    """Edit account details. At the moment, only the full name is eligable for edit

    Args:
        username (str | None, optional): Username of user account to edit. If none, edit self's account.

    Raises:
        NotLoggedIn: If token is expired or not there, raise custom exception
    """

    # check token
    token = get_token()
    if token is None or api.check_token(token) is False:
        raise NotLoggedIn

    if username is None:
        username = api.get_username(token)

    # get latest data from api
    user = api.get_user(token, username)
    if user is None:
        console.print("User does not exist\n", style="danger")
        return

    # get input
    new_full_name = str(input(f"Full name[{user.full_name}]: "))
    if new_full_name == "":
        console.print("\nNothing was changed\n")
        return

    # api call
    user.full_name = new_full_name
    try:
        rc = api.put_user(token, user)

    except NotAdmin:
        console.print("\nYou cannot edit someone else's account\n", style="danger")
        return

    if rc == 1:
        console.print("\nCould not edit user\n", style="danger")
        return
    if rc == 2:
        console.print("\nCould not find user\n", style="danger")
        return

    console.print("\nUser edited successfully\n", style="success")


def show_user(
    username: str | None = None, console: Console = console, api: API = api
) -> None:
    """Get user data from API

    Args:
        username (str | None, optional): Username of user to get data of. If none, get user data of self.

    Raises:
        NotLoggedIn: invalid token
    """

    # check token
    token = get_token()
    if token is None or api.check_token(token) is False:
        raise NotLoggedIn

    # input
    if username is None:
        username = api.get_username(token)

    # api call
    user = api.get_user(token, username)

    if user is None:
        console.print("User not found\n", style="danger")
        return

    print_user(user, console)


def search_user(username: str, console: Console = console, api: API = api) -> None:
    """Query users by username

    Args:
        username (str): username to query by

    Raises:
        NotLoggedIn: invalid token
    """

    # check token
    token = get_token()
    if token is None or api.check_token(token) is False:
        raise NotLoggedIn

    # api call
    query = api.get_multiple_users(token, username)

    # data handling
    if len(query) == 0:
        console.print("Could not find anyone with that username\n", style="warning")
        return

    print_search_users(query)


def print_user(user: User, console: Console) -> None:
    """Function to properly print user data

    Args:
        user (User): user data
        console (Console): Rich console
    """

    color = choice(["red", "blue", "green", "cyan", "purple", "magenta", "yellow"])
    if user.profile_picture is not None:
        pfp = Panel.fit(
            user.profile_picture, border_style=color, title="Profile picture"
        )
        console.print(pfp)
    console.print(
        Panel.fit(
            f"\n[{color}]Username:[/] {user.username}\n\n[{color}]Full Name:[/] {user.full_name}",
            border_style=color,
            title=f"{user.username}'s details",
        ),
    )
    console.print()  # a bit of space


def print_search_users(query: list) -> None:
    """Function to properly print user search results"""

    color = choice(["red", "blue", "green", "cyan", "purple", "magenta", "yellow"])
    results = Text("\n\n".join(query), justify="center")

    console.print(
        Panel.fit(
            f"\n[{color}]{results}[/]\n",
            border_style=color,
            title="Search Results",
        ),
    )
    console.print()  # a bit of space


def user(
    function: str,
    username: str | None = None,
) -> callable:
    """Parent function to combine all user function

    Args:
        function (str, optional): Which function to use. Defaults to None (to avoid exception).
        username (str | None, optional): Username of account to work on. If none, work on self's account.

    Returns:
        callable: the respective account function
    """

    match function:
        case "edit":
            return edit_user(username)
        case "delete":
            return delete_user(username)
        case "show":
            return show_user(username)
        case "search":
            return search_user(username)
        case _:
            raise AttributeError


def make_admin(username: str, console: Console = console, api: API = api) -> None:
    """Make another user an admin (must be an admin yourself)

    Args:
        username (str): username of user to promote to admin

    Raises:
        NotLoggedIn: invalid token
    """

    # check token
    token = get_token()
    if token is None or api.check_token(token) is False:
        raise NotLoggedIn

    try:
        rc = api.make_admin(token, username)

    except NotAdmin:
        console.print("You have to be an admin to use this command\n", style="danger")
        return

    if rc == 1:
        console.print("Could not promote user\n", style="danger")
        return
    if rc == 2:
        console.print("User not found\n", style="warning")
        return

    console.print("User promoted successfully\n", style="success")
