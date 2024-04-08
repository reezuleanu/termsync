from rich.console import Console
import json
import yaml
from bson import json_util, BSON
import platform
from os import system
from .exceptions import NotLoggedIn


# ! OBSOLETE
def bson2dict(bson: BSON) -> dict:
    """Function which converts bson data (like a mongodb query)"""

    return json.loads(json_util.dumps(bson))


# ! OBSOLETE
def result_get_id(result) -> str:
    """Function which retrieves the id from the response of ".insert_one()"

    Args:
        result (InsertOneResult): whatever pymongo's ".insert_one()" retrieves

    Returns:
        str: the id in plain text, like God intended
    """

    return json.loads(json_util.dumps(result.inserted_id))["$oid"]


def replace(list: list, value: any, replacement: any) -> None:
    """Replace the value in any list by the replacement

    Args:
        list (list): reference to list
        value (any): value to be replaced
        replacement (any): value to be replaced with
    """

    index: int = list.index(value)
    list[index] = replacement


def clear_screen() -> None:
    """System call to clear screen"""

    os = platform.system()

    if os == "Windows":
        system("cls")
    else:
        system("clear")


def get_token() -> str:
    """Get token from session.json

    Returns:
        str: token
    """

    token: str = None
    try:
        with open("data/session.json", "r") as fp:
            token = json.load(fp)["token-uuid"]

    except json.decoder.JSONDecodeError or FileNotFoundError:
        token = None
        # return token

    finally:
        # for whatever reason it threw an unbound error even if it was defined in both try and except
        return token

    # if token is None:
    #     raise NotLoggedIn

    # return token


def get_username() -> str:
    """Get username from session.json

    Returns:
        str: username
    """

    username: str = None
    try:
        with open("data/session.json", "r") as fp:
            username = json.load(fp)["username"]

    except json.decoder.JSONDecodeError or FileNotFoundError:
        username = None

    finally:
        return username

    # if username is None:
    #     raise NotLoggedIn

    # return username


def get_settings(setting_name: str) -> str:

    setting: str = None
    try:
        with open("data/settings.yaml", "r") as fp:
            setting = yaml.safe_load(fp)[setting_name]

    except (KeyError, FileNotFoundError):
        with open("data/settings.yaml", "w") as fp:
            # default values
            HOST = "127.0.0.1"
            PORT = 2727
            settings = {"HOST": HOST, "PORT": PORT}
            yaml.safe_dump(settings, fp)

            try:
                setting = settings[setting_name]
            except KeyError:
                print("Wrong setting name")

    finally:
        return setting


def write_update_cache(*to_update: str) -> None:

    try:
        fp = open("data/update_cache.txt", "r")
        cache = fp.read().split("\n")
        fp.close()
    except FileNotFoundError:
        pass

    for update in to_update:
        if update not in cache:
            cache.append(update)

    with open("data/update_cache.txt", "w") as fp:
        fp.write("\n".join(cache))


def wipe_update_cache() -> None:

    try:
        fp = open("data/update_cache.txt", "w")
    except FileNotFoundError:
        return

    fp.write("")
    fp.close()


def read_update_cache() -> list:

    try:
        fp = open("data/update_cache.txt", "r")
    except FileNotFoundError:
        return []

    return fp.read().split("\n")


def pop_update_cache(updating: str) -> None:

    fp = open("data/update_cache.txt", "r")

    cache = fp.read().split("\n")

    fp.close()

    if updating in cache:
        cache.pop(cache.index(updating))

    fp = open("data/update_cache.txt", "w")

    if len(cache) > 0:
        fp.write("\n".join(cache))
    else:
        fp.write("")

    fp.close()
