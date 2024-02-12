from bson import json_util, BSON
import json

# apparently this doesn't work
# from pymongo import InsertOneResult


def bson2dict(bson: BSON) -> dict:
    """Function which converts bson data (like a mongodb query)"""

    return json.loads(json_util.dumps(bson))


def result_get_id(result) -> str:
    """Function which retrieves the id from the response of ".insert_one()"

    Args:
        result (InsertOneResult): whatever pymongo's ".insert_one()" retrieves

    Returns:
        str: the id in plain text, like God intended
    """

    return json.loads(json_util.dumps(result.inserted_id))["$oid"]
