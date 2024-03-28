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

    # logo text
    logo = Text(
        """
$$$$$$$$\                                 $$$$$$\                                
\__$$  __|                               $$  __$$\                               
   $$ | $$$$$$\   $$$$$$\  $$$$$$\$$$$\  $$ /  \__|$$\   $$\ $$$$$$$\   $$$$$$$\ 
   $$ |$$  __$$\ $$  __$$\ $$  _$$  _$$\ \$$$$$$\  $$ |  $$ |$$  __$$\ $$  _____|
   $$ |$$$$$$$$ |$$ |  \__|$$ / $$ / $$ | \____$$\ $$ |  $$ |$$ |  $$ |$$ /      
   $$ |$$   ____|$$ |      $$ | $$ | $$ |$$\   $$ |$$ |  $$ |$$ |  $$ |$$ |      
   $$ |\$$$$$$$\ $$ |      $$ | $$ | $$ |\$$$$$$  |\$$$$$$$ |$$ |  $$ |\$$$$$$$\ 
   \__| \_______|\__|      \__| \__| \__| \______/  \____$$ |\__|  \__| \_______|
                                                   $$\   $$ |                    
                                                   \$$$$$$  |                    
                                                    \______/                     
""",
        justify="left",
        style=f"bold {color}",
    )

    # display logo
    console.print(Panel.fit(logo, border_style=color), justify="center")
