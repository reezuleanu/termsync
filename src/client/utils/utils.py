import json
from bson import json_util, BSON
from os import system


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

    index = list.index(value)
    list[index] = replacement


def clear_screen(*args) -> None:
    """System call to clear screen"""

    system("clear")


def get_token() -> str:
    """Get token from session.json

    Returns:
        str: token
    """

    token = None
    try:
        with open("data/session.json", "r") as fp:
            token = json.load(fp)["token-uuid"]

    except json.decoder.JSONDecodeError or FileNotFoundError:
        # token = None
        return token

    finally:
        # for whatever reason it threw an unbound error even if it was defined in both try and except
        return token


def get_username() -> str:
    """Get username from session.json

    Returns:
        str: username
    """

    try:
        with open("data/session.json", "r") as fp:
            username = json.load(fp)["username"]

    except json.decoder.JSONDecodeError or FileNotFoundError:
        username = None

    finally:
        return username
