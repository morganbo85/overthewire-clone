from fastapi import FastAPI, Depends
from pydantic import BaseModel
import hashlib

app = FastAPI()

# Dummy user storage (use Postgres later)
users = {"bo": {"password": "testpass", "score": 0}}

# Store flag hashes
flags = {
    "level1": hashlib.sha256("FLAG{this_is_level1}".encode()).hexdigest()
}

class SubmitFlag(BaseModel):
    username: str
    password: str
    level: str
    flag: str

@app.post("/submit")
def submit_flag(data: SubmitFlag):
    if data.username not in users or users[data.username]["password"] != data.password:
        return {"status": "error", "message": "Invalid login"}

    hashed = hashlib.sha256(data.flag.encode()).hexdigest()
    if data.level in flags and flags[data.level] == hashed:
        users[data.username]["score"] += 10
        return {"status": "ok", "message": "Correct flag!", "score": users[data.username]["score"]}
    return {"status": "error", "message": "Wrong flag"}
