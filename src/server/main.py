from fastapi import FastAPI, Request
from uuid import UUID
import logging
import datetime


from .routers import helloworld, login, projects, users
from .dependencies import token_auth, db_depend

# initiate app
app = FastAPI()
app.title = "TermSync"
app.description = "Server for novelty CLI project organizational tool"

# add routers
app.include_router(users.router)
app.include_router(helloworld.router)
app.include_router(login.router)
app.include_router(projects.router)

# setup logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

formatter = logging.Formatter(fmt="[%(asctime)s]: %(message)s")

file_handler = logging.FileHandler(f"src/server/logs/{datetime.datetime.now().date()}")
file_handler.setFormatter(formatter)

logger.handlers = [file_handler]


# add middleware
@app.middleware("http")
async def api_logger(request: Request, call_next):

    # get basic data from request
    log = {
        "time": "time",
        "url": request.url.path,
        "method": request.method,
    }

    # try to get token if there is any
    try:
        log["token-uuid"] = request.headers["token-uuid"]

        # convert token to username
        username = token_auth(
            token_uuid=UUID(log["token-uuid"]), db=db_depend()
        ).username
        log["username"] = username

    except KeyError:
        pass

    # await response
    response = await call_next(request)

    # insert response status code into log
    log["response-code"] = response.status_code

    logger.info(log)

    return response
