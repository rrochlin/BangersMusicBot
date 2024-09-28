from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
import uuid
from datetime import datetime

Base = declarative_base()


# class Account(Base):
#     __tablename__ = 'Account'
#     id = Column(String, nullable=False, primary_key=True)
#     userId = Column(String, nullable=False, index=True)
#     type = Column(String, nullable=False)
#     provider = Column(String, nullable=False)
#     providerAccountId = Column(String, nullable=False, index=True)
#     refresh_token = Column(String, nullable=False)
#     access_token = Column(String, nullable=False)
#     expires_at = Column(Integer, nullable=False)
#     token_type = Column(String, nullable=True)
#     scope = Column(String, nullable=True)
#     id_token = Column(String, nullable=True)
#     session_state = Column(String, nullable=True)


class Song(Base):
    __tablename__ = "Song"
    id = Column(Integer, nullable=False, primary_key=True)
    title = Column(String, nullable=False, index=True)
    url = Column(String, nullable=False, index=True)
    source = Column(String, nullable=False, index=True)
    thumbnail = Column(String, nullable=False)
    createdAt = Column(DateTime, nullable=False, default=datetime.now())
    updatedAt = Column(DateTime, nullable=False, default=datetime.now())
    createdById = Column(String, nullable=False, index=True)


class Queue(Base):
    __tablename__ = "Queue"
    id = Column(Integer, nullable=False, primary_key=True)
    title = Column(String, nullable=False, index=True)
    url = Column(String, nullable=False, index=True)
    source = Column(String, nullable=False, index=True)
    thumbnail = Column(String, nullable=False)
    createdAt = Column(DateTime, nullable=False, default=datetime.now())
    updatedAt = Column(DateTime, nullable=False, default=datetime.now())
    createdById = Column(String, nullable=False, index=True)


class PlaylistPointer(Base):
    def from_queue(queue: Queue):
        return PlaylistPointer(
            id=queue.id,
            title=queue.title,
            url=queue.url,
            source=queue.source,
            thumbnail=queue.thumbnail,
            createdAt=queue.createdAt,
            updatedAt=queue.updatedAt,
            createdById=queue.createdById
            )
    __tablename__ = "PlaylistPointer"
    id = Column(Integer, nullable=False, primary_key=True)
    title = Column(String, nullable=False, index=True)
    url = Column(String, nullable=False, index=True)
    source = Column(String, nullable=False, index=True)
    thumbnail = Column(String, nullable=False)
    createdAt = Column(DateTime, nullable=False, default=datetime.now())
    updatedAt = Column(DateTime, nullable=False, default=datetime.now())
    createdById = Column(String, nullable=False, index=True)

# class Session(Base):
#     __tablename__ = "Session"
#     id = Column(String, nullable=False, primary_key=True)
#     sessionToken = Column(String, nullable=False, index=True)
#     userId = Column(String, nullable=False, index=True)
#     expires = Column(DateTime, nullable=False)


class User(Base):
    __tablename__ = "User"
    id = Column(String, nullable=False, primary_key=True, default=uuid.uuid1().__str__())
    name = Column(String, nullable=True)
    email = Column(String, nullable=True, index=True)
    emailVerified = Column(DateTime, nullable=True)
    image = Column(String, nullable=True)


# class VerificationToken(Base):
#     __tablename__ = "VerificationToken"
#     identifier = Column(String, nullable=False, index=True)
#     token = Column(String, nullable=False, index=True)
#     expires = Column(DateTime, nullable=False)
