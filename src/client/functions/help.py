from rich.console import Console
from rich.panel import Panel
from ui import console

# instructions manual
manual = {
    "register": {"syntax": "register", "description": "create a new account"},
    "login": {
        "syntax": "login \[optional username]",
        "description": "login with an an already existing account",
        "args": {"\[username]": "optional username"},
    },
    "disconnect": {
        "syntax": "disconnect",
        "description": "disconnect from your current account",
    },
    "exit": {"syntax": "exit", "description": "exit the app"},
    "test": {"syntax": "test", "description": "test command"},
}


def help(command: str = None, console: Console = console) -> None:
    """Function that returns instructions about how to use a command. Prints all commands and descriptions.
    If providing a specific command, it will print a more in depth description

    Args:
        command (str, optional): Specific command to print instructions for. Defaults to None.
        console (Console, optional): Rich Console. Defaults to console.
    """

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
