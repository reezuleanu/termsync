from fastapi import FastAPI
from routers import user, helloworld, login


# initiate app
app = FastAPI()
app.title = "TermSync"
app.description = "Server for novelty CLI project organizational tool"

# add routers
app.include_router(user.router)
app.include_router(helloworld.router)
app.include_router(login.router)
