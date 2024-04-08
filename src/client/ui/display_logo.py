from rich.text import Text
from rich.panel import Panel
from rich.console import Console
from random import choice


def display_logo(console: Console) -> None:
    """Print app logo to the console

    Args:
        console (Console): rich console
    """

    # random logo color
    color = choice(["red", "blue", "green", "cyan", "purple", "magenta", "yellow"])

    # load logo text
    with open("ui/logo.txt", "r") as fp:
        logo = fp.read()

    logo = Text(logo, justify="left", style=f"bold {color}")

    # display logo
    console.print(Panel.fit(logo, border_style=color), justify="center")
