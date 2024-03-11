# global imports
from fastapi import APIRouter, Depends

# relative imports
from ..models import User
from ..dependencies import token_auth, admin_auth

# init router
router = APIRouter()


@router.get("/")
def hello(user: User = Depends(token_auth), admin: bool = Depends(admin_auth)) -> dict:
    """Simple Hello World API call

    Returns:
        dict: API response
    """

    return {"response": f"hello there {user.username}!", "admin": admin}
