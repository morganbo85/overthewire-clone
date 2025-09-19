import os
import time
import hashlib
import logging
from typing import Dict, List
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from starlette.responses import JSONResponse

# Basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend")

app = FastAPI()

# Simple in-memory user store -> replace with Postgres in prod
users = {"bo": {"password": "testpass", "score": 0}}

# Use an environment salt for flag hashing (set in docker-compose env)
FLAG_SALT = os.environ.get("FLAG_SALT", "change_this_now")

def salted_hash(s: str) -> str:
    return hashlib.sha256((FLAG_SALT + s).encode()).hexdigest()

# Store salted hashes of flags
flags = {
    "level1": salted_hash("FLAG{this_is_level1}")
}

class SubmitFlag(BaseModel):
    username: str
    password: str
    level: str
    flag: str

# Rate limiter storage: { ip: [timestamps...] }
_rate_limiter: Dict[str, List[float]] = {}
RATE_LIMIT = 10           # allowed attempts
RATE_PERIOD = 60.0        # per seconds (sliding window)

def is_rate_limited(ip: str) -> bool:
    now = time.time()
    window_start = now - RATE_PERIOD
    timestamps = _rate_limiter.get(ip, [])

    # keep only timestamps in window
    timestamps = [t for t in timestamps if t >= window_start]
    _rate_limiter[ip] = timestamps

    if len(timestamps) >= RATE_LIMIT:
        return True

    # record this attempt
    _rate_limiter[ip].append(now)
    return False

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    # Example middleware; you can extend for logging
    response = await call_next(request)
    return response

@app.post("/submit")
async def submit_flag(request: Request, data: SubmitFlag):
    client_ip = request.client.host

    if is_rate_limited(client_ip):
        logger.warning("Rate-limited submit attempt from %s", client_ip)
        raise HTTPException(status_code=429, detail="Too many attempts. Slow down.")

    # auth (move to hashed password + DB in prod)
    user = users.get(data.username)
    if not user or user["password"] != data.password:
        logger.info("Invalid login attempt for user=%s from %s", data.username, client_ip)
        raise HTTPException(status_code=401, detail="Invalid login")

    hashed = salted_hash(data.flag)
    target = flags.get(data.level)
    if target and hashed == target:
        user["score"] += 10
        logger.info("Correct flag for %s by %s", data.level, data.username)
        return JSONResponse({"status": "ok", "message": "Correct flag!", "score": user["score"]})
    logger.info("Wrong flag for %s by %s from %s", data.level, data.username, client_ip)
    raise HTTPException(status_code=400, detail="Wrong flag")
