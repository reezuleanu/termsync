from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from random import choice
import getpass
import json
from rich.layout import Layout
from ui import console
from models import User
from api import API, api
from utils import get_token, NotLoggedIn, NotAdmin


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

    new_user = User(username=username, full_name=full_name)

    # api call and token serialization
    token = api.post_project(new_user, password)

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

    password = str(getpass.getpass("\nPassword: "))

    # login call
    token = api.login(username, password)

    # if call is not successfull
    if token is None:
        console.print("\nWrong username or password\n", style="danger")
        return

    # save token
    with open("data/session.json", "w") as fp:
        json.dump({"token-uuid": token, "username": username}, fp)

    console.print("\nLogin successful\n", style="success")


def delete_account(
    username: str | None = None, console: Console = console, api: API = api
) -> None:
    """Delete account. Upon deletion, app exits

    Args:
        username (str | None, optional): username of account to delete. If provided, it won't ask you for the username again. Defaults to None.
        console (Console, optional): Rich console. Defaults to console.
        api (API, optional): API interface. Defaults to api.

    Raises:
        NotLoggedIn: if not logged in
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

    console.print("\nAccount deleted sucessfully\n", style="success")
    console.print("Press any key to exit\n")
    input()
    raise KeyboardInterrupt


def edit_account(
    username: str | None = None, console: Console = console, api: API = api
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
        console.print("\nUser does not exist\n", style="danger")
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

    console.print("\nUser edited successfully\n", style="success")


def account(
    function: str = None,
    username: str | None = None,
    console: Console = console,
    api: API = api,
) -> callable:
    """Parent function to combine edit_account() and delete_account()

    Args:
        function (str, optional): Which function to use. Defaults to None (to avoid exception).
        username (str | None, optional): Username of account to work on. If none, work on self's account.

    Returns:
        callable: the respective account function
    """

    if function == "edit":
        return edit_account(username)
    elif function == "delete":
        return delete_account(username)
    else:
        console.print(
            "\nIncorrect usage, please use 'help account' for instructions.\n",
            style="warning",
        )


def get_user(
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

    if username is None:
        username = api.get_username(token)

    user = api.get_user(token, username)

    if user is None:
        console.print("\nUser not found\n", style="danger")
        return

    print_user(user, console)


def print_user(user: User, console: Console) -> None:

    # todo implement print user data function
    console.print()
    console.print(user.model_dump())
    console.print()


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
        console.print("\nYou have to be an admin to use this command\n", style="danger")
        return

    if rc == 1:
        console.print("\nCould not promote user\n", style="danger")
        return
    if rc == 2:
        console.print("\nUser not found\n", style="warning")
        return
    console.print("\nUser promoted successfully\n", style="success")


def test(console: Console = console) -> None:
    """Test function, please ignore"""

    i = {"username": "bob", "full_name": "bob the builder"}
    i["username"] = f"[yellow]{i['username']}[/yellow]"
    # for key in i.keys():
    #     console.print(f"\n[white]{key} : {i[key]}[/]", justify="center")
    # console.print()

    amogus = Text(
        """                                                                   
                 *@%**##%@@#               
                #%+++++++++#@*             
               =@+++#@@@##*#%@%            
               @#+++@+.        %           
           +@@@@#+++@-:.       *@          
           @++#@*+++%@+-::::-=*@+          
           @*+%@*++++#@@@@@@@%@=           
          :@++%@*+++++++++++++%%           
          :%++%@*+++++++++++++#@           
          :%++%@*+++++++++++++%#           
           @*+#@*+++++++++++++@-           
           -@@@@#++++*@%***#+*@.           
               @#++++@@:@@+++%%            
               @#++++@% #%+++%*            
                @%**@@.   =-:               """,
        justify="center",
    )

    color = choice(["red", "blue", "green", "cyan", "purple", "magenta", "yellow"])

    pfp = Panel.fit(amogus, border_style=color, title="Profile picture")
    console.print(pfp)
    console.print(
        Panel.fit(
            f"\nUsername: {'bob'}\n\nFull Name: {'bob the sussy'}",
            border_style=color,
            title="Bob's details",
        ),
    )
    console.print()
