class NotLoggedIn(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class NotAdmin(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
