from rich import print
from rich.panel import Panel
from rich.console import Console
from rich.text import Text
from ui import console, display_logo
from os import system
from rich.layout import Layout
from functions import startup


if __name__ == "__main__":
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
        system("clear")
        startup(console)

        while True:
            continue
    except KeyboardInterrupt:
        system("clear")
        print("ok mam kalmat\n\n")
