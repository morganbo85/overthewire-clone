import os, time, hashlib, logging, json
from typing import List, Dict
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from passlib.hash import bcrypt
from sqlalchemy.exc import OperationalError

from models import Base, User, Level, Submission

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("backend")

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./game.db")
FLAG_SALT = os.environ.get("FLAG_SALT", "change_me_now")

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(engine, expire_on_commit=False, future=True)

def salted_hash(s: str) -> str:
    return hashlib.sha256((FLAG_SALT + s).encode()).hexdigest()

# simple in-memory rate limiter
_RATE: Dict[str, List[float]] = {}
RATE_LIMIT = 10
RATE_PERIOD = 60.0

def rate_limited(ip: str) -> bool:
    now = time.time()
    arr = [t for t in _RATE.get(ip, []) if t > now - RATE_PERIOD]
    _RATE[ip] = arr
    if len(arr) >= RATE_LIMIT:
        return True
    _RATE[ip].append(now)
    return False

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class RegisterIn(BaseModel):
    username: str
    password: str

class LoginIn(BaseModel):
    username: str
    password: str

class SubmitIn(BaseModel):
    username: str
    password: str
    flag: str

def seed_levels_from_json(db: Session):
    """Seed or update levels table from levels.json."""
    path = os.path.join(os.path.dirname(__file__), "levels.json")
    if not os.path.exists(path):
        log.warning("levels.json not found, skipping level seeding")
        return

    with open(path, "r") as f:
        levels = json.load(f)

    for lvl in levels:
        hashed = salted_hash(lvl["flag"])
        existing = db.get(Level, lvl["id"])
        if existing:
            existing.name = lvl["name"]
            existing.flag_hash = hashed
            existing.points = lvl.get("points", 0)
        else:
            db.add(Level(
                id=lvl["id"],
                name=lvl["name"],
                flag_hash=hashed,
                points=lvl.get("points", 0)
            ))
    db.commit()
    log.info("Seeded %d levels from levels.json", len(levels))

@app.on_event("startup")
def on_startup():
    # retry DB connection
    for i in range(10):
        try:
            Base.metadata.create_all(engine)
            break
        except OperationalError:
            log.warning("DB not ready, retrying in 3s...")
            time.sleep(3)
    else:
        raise RuntimeError("Database never came up")

    with SessionLocal() as db:
        seed_levels_from_json(db)

        # optional initial admin/user
        init = os.environ.get("INITIAL_ADMIN")
        if init:
            uname, pwd = init.split(":", 1)
            if not db.query(User).filter_by(username=uname).first():
                db.add(User(
                    username=uname,
                    password_hash=bcrypt.hash(pwd),
                    score=0,
                    current_level=1
                ))
                db.commit()
                log.info("Created initial admin %s", uname)

@app.post("/register")
def register(data: RegisterIn, request: Request, db=Depends(get_db)):
    if rate_limited(request.client.host):
        raise HTTPException(429, "Too many attempts")
    if db.query(User).filter_by(username=data.username).first():
        raise HTTPException(400, "Username exists")
    u = User(username=data.username, password_hash=bcrypt.hash(data.password), score=0, current_level=1)
    db.add(u)
    db.commit()
    return {"status": "ok", "message": "registered"}

@app.post("/login")
def login(data: LoginIn, request: Request, db=Depends(get_db)):
    if rate_limited(request.client.host):
        raise HTTPException(429, "Too many attempts")
    u = db.query(User).filter_by(username=data.username).first()
    if not u or not bcrypt.verify(data.password, u.password_hash):
        raise HTTPException(401, "Invalid credentials")
    return {"status": "ok", "username": u.username, "current_level": u.current_level, "score": u.score}

@app.get("/progress")
def progress(username: str, request: Request, db=Depends(get_db)):
    if rate_limited(request.client.host):
        raise HTTPException(429, "Too many attempts")
    u = db.query(User).filter_by(username=username).first()
    if not u:
        raise HTTPException(404, "User not found")
    return {"username": u.username, "current_level": u.current_level}

@app.post("/submit")
def submit(data: SubmitIn, request: Request, db=Depends(get_db)):
    if rate_limited(request.client.host):
        raise HTTPException(429, "Too many attempts")

    u = db.query(User).filter_by(username=data.username).first()
    if not u or not bcrypt.verify(data.password, u.password_hash):
        raise HTTPException(401, "Invalid credentials")

    L = db.get(Level, u.current_level)
    if not L:
        raise HTTPException(400, "Level not configured")

    ok = (salted_hash(data.flag) == L.flag_hash)
    db.add(Submission(user_id=u.id, level_id=L.id, flag_text=data.flag, correct=ok))
    db.commit()

    if not ok:
        raise HTTPException(400, "Wrong flag")

    u.score += L.points
    u.current_level = u.current_level + 1
    db.commit()
    log.info("User %s advanced to level %d (score=%d)", u.username, u.current_level, u.score)
    return {"status": "ok", "message": "Correct flag! Advanced.", "next_level": u.current_level, "score": u.score}

# Serve static GUI under /gui
app.mount("/gui", StaticFiles(directory="static", html=True), name="static")