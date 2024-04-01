from ui import console
from utils import clear_screen
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

        while True:
            clear_screen()
            startup(console)
    except KeyboardInterrupt:
        clear_screen()
