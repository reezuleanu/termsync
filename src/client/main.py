from app import App
from api import api
from ui import console


app = App(console, api)

app.run()
