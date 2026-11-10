from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from database import create_db_and_tables, get_session
from models import User, Event, Registration

#TaskD2
class UserCreate(BaseModel):
    email: str
    role: str = "student"


class EventCreate(BaseModel):
    title: str
    description: str
    venue: str
    start_time: datetime
    capacity: int
    organizer_id: int


#TaskD1
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/events", response_model=list[Event])
def list_events(session: Session = Depends(get_session)):
    return session.exec(select(Event)).all()