from fastapi import APIRouter, Request, HTTPException

router = APIRouter()


@router.get("/")
def hello(request: Request) -> dict:
    """Simple Hello World API call

    Args:
        request (Request): header should contain "token" token

    Returns:
        dict: server response
    """
    token = request.headers["token"]
    if token != "213":
        raise HTTPException(403, "Unauthorized access")
    return {"response": "hello there!"}
