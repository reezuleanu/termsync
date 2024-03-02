# global imports
from fastapi import APIRouter, Depends

# relative imports
from ..models import Token
from ..dependencies import token_auth, db_depend
from ..database import Database

# init router
router = APIRouter()


@router.get("/")
def hello(
    token: Token = Depends(token_auth), db: Database = Depends(db_depend)
) -> dict:
    """Simple Hello World API call

    Args:
        token (Token): User Token
        db (Database): database

    Returns:
        dict: API response
    """

    return {"response": "hello there!", "token": token}
