from rich.console import Console
from rich.panel import Panel
from ui import console
import json


def help(command: str = None, console: Console = console) -> None:
    """Function that returns instructions about how to use a command. Prints all commands and descriptions.
    If providing a specific command, it will print a more in depth description

    Args:
        command (str, optional): Specific command to print instructions for. Defaults to None.
        console (Console, optional): Rich Console. Defaults to console.
    """
    try:
        with open("functions/manual.json", "r") as fp:
            manual = json.load(fp)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        console.print("Could not load commands manual\n", style="danger")
        return

    # no specific command provided
    if command is None:
        console.print(Panel.fit("Commands"))
        console.print()
        for key in manual.keys():
            console.print(f"  {key} : {manual[key]['description']}\n")

    # specific command provided and is in manual
    elif command in manual.keys():
        console.print(Panel.fit(manual[command]["syntax"]))
        console.print()
        console.print(f"  Description: {manual[command]['description']}\n")

        if "args" in manual[command].keys():
            console.print("  Args:\n")
            for arg in manual[command]["args"].keys():
                console.print(f"  {arg} : {manual[command]['args'][arg]}\n")

    # provided specific command that doesn't exist
    else:
        console.print(
            "No such command available. Try 'help' to see all available commands\n",
            style="danger",
        )

    # unload manual, just in case the garbage collector doesn't
    manual = None
