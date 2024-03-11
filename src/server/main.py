from fastapi import FastAPI
from mongomock import MongoClient
from .routers import helloworld, login, projects, users
from .database import Database
from .dependencies import db_depend

# initiate app
app = FastAPI()
app.title = "TermSync"
app.description = "Server for novelty CLI project organizational tool"

# add routers
app.include_router(users.router)
app.include_router(helloworld.router)
app.include_router(login.router)
app.include_router(projects.router)
