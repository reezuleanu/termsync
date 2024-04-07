"""Module containing all server utils"""

from .utils import (
    bson2dict,
    result_get_id,
    replace,
    clear_screen,
    get_token,
    get_username,
    get_settings,
)

from .exceptions import NotAdmin, NotLoggedIn
