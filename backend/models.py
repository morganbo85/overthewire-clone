from sqlalchemy import Column, Integer, String, Boolean, Text, TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    ssh_publickey = Column(Text)
    score = Column(Integer, default=0, nullable=False)
    current_level = Column(Integer, default=1, nullable=False)

class Level(Base):
    __tablename__ = "levels"
    id = Column(Integer, primary_key=True)         # 1,2,3,...
    name = Column(String, nullable=False)
    flag_hash = Column(String, nullable=False)      # salted hash
    points = Column(Integer, default=10, nullable=False)

class Submission(Base):
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    level_id = Column(Integer, ForeignKey("levels.id"), nullable=False)
    flag_text = Column(Text, nullable=False)
    correct = Column(Boolean, default=False, nullable=False)
    timestamp = Column(TIMESTAMP, server_default=func.now())
    user = relationship("User")
    level = relationship("Level")
