from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
import redis
import secrets

app = FastAPI()


class Url(BaseModel):
    url: str


redis_conn = redis.Redis(host="127.0.0.1", port=6379, db=0)

BASE_URL = "http://localhost:8000/"


@app.get("/")
async def root(url: Url):
    return {"message": "Hello World"}


@app.post("/shorten")
async def shorten_url(url: Url):
    while True:
        short_id = secrets.token_urlsafe(5)
        if not redis_conn.exists(short_id):
            redis_conn.set(short_id, url.url)
            break
    return {"short_id": short_id, "url": f"{BASE_URL}/{short_id}"}


@app.get("/{short_id}")
async def redirect_url(short_id: str):
    url = redis_conn.get(short_id)
    if url:
        return RedirectResponse(url.decode())
    else:
        return {"message": "URL not found"}
