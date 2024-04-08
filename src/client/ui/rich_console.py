from rich.console import Console
from rich.theme import Theme

# rich console and themes used in app
theme = Theme({"danger": "bold red", "warning": "bold yellow", "success": "bold green"})
console = Console(theme=theme)
