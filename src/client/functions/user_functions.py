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


def register(*args, console: Console = console, api: API = api) -> str:
    """Create new account functionality

    Args:
        console (Console, optional): Rich console. Defaults to console.
        api (API, optional): API interface. Defaults to api.

    Returns:
        str: username
    """

    # gather data
    username = str(input("Enter username: "))
    full_name = str(input("\nEnter full name: "))
    password = str(getpass.getpass("\nEnter password: "))

    new_user = User(username=username, full_name=full_name)

    # api call and token serialization
    token = api.register(new_user, password)

    if token is None:
        console.print("\nCould not create new user", style="danger")
        return

    with open("data/session.json", "w") as fp:
        json.dump({"token-uuid": token}, fp)

    console.print("\nUser created successfully\n", style="success")
    return api.get_username(token)


def login(username: str = None, console: Console = console, api: API = api) -> str:
    """Login functionality

    Args:
        username (str, optional): If username is provided with the command, the user will be asked only for the password. Defaults to None.
        console (Console, optional): Rich console. Defaults to console.
        api (API, optional): API interface. Defaults to api.

    Returns:
        str: username
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
        json.dump({"token-uuid": token}, fp)

    console.print("\nLogin successful\n", style="success")
    return api.get_username(token)


def delete_account(username: str, hashed_password: str) -> int:
    raise NotImplementedError


def edit_account() -> int:
    raise NotImplementedError


def get_user() -> User:
    raise NotImplementedError


def make_admin() -> int:
    raise NotImplementedError


def test(console: Console = console) -> None:
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
            f"\nUsername: {'bob'}\n\nFull Name: {'bob the builder'}",
            border_style=color,
            title="Bob's details",
        ),
    )
    console.print()
