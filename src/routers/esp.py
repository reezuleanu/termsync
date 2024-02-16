from fastapi import APIRouter, HTTPException
import requests


router = APIRouter()

esp_url = "http://192.168.0.10"


@router.get("/esp")
def esp() -> dict:
    response = requests.get(f"{esp_url}/12/on")
    if response.status_code == 200:
        return {"response": "memeing has started successfully"}
    else:
        raise HTTPException(503)
