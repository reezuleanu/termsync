from datetime import datetime
from time import sleep
from rich.console import Console


commands = {"login": print, "register": print}


def prompt(console: Console, username: str) -> None:
    while True:
        console.print(f"[{datetime.now()}]", end="")
        command = input(f"[{username}] >> ")
        if command in commands:
            commands[command](command)
        elif command == "":
            print()
        else:
            print("Bad command")
