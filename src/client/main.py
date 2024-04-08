import threading
from app import App
from api import api
from ui import console
from utils import clear_screen

app = App(console, api)

# main thread
t1 = threading.Thread(target=app.run)

# daemon thread handling connection status and project updates
t2 = threading.Thread(target=app.get_update, daemon=True)

threads = [t1, t2]


if __name__ == "__main__":
    try:
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

    except KeyboardInterrupt:
        clear_screen()
