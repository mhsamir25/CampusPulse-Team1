from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status, Query
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


##Task E1
@app.post("/users", response_model=User, status_code=201)
def create_user(data: UserCreate, session: Session = Depends(get_session)):
    user = User(email=data.email, role=data.role)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


#Task E2
@app.post("/events", response_model=Event, status_code=status.HTTP_201_CREATED)
def create_event(data: EventCreate, session: SessionDep):
    if data.capacity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Capacity must be greater than zero",
        )

    organizer = session.get(User, data.organizer_id)
    if not organizer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organizer with id {data.organizer_id} does not exist",
        )

    event = Event(**data.model_dump())
    session.add(event)
    session.commit()
    session.refresh(event)
    return event

#Task E3
@app.get("/events", response_model=list[Event])
def list_events(
    session: SessionDep,
    venue: str | None = Query(default=None, description="Filter events by venue substring"),
):
    query = select(Event)
    if venue:
        query = query.where(Event.venue.contains(venue))
    return session.exec(query).all()


@app.get("/events/{event_id}", response_model=Event)
def get_event(event_id: int, session: SessionDep):
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with id {event_id} not found",
        )
    return event

## Task E4
@app.put("/events/{event_id}", response_model=Event)
def update_event(event_id: int, data: EventCreate, session: SessionDep):
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with id {event_id} not found",
        )

    if data.capacity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Capacity must be greater than zero",
        )

    organizer = session.get(User, data.organizer_id)
    if not organizer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organizer with id {data.organizer_id} does not exist",
        )

    for key, value in data.model_dump().items():
        setattr(event, key, value)

    session.add(event)
    session.commit()
    session.refresh(event)
    return event

## Task E5
@app.delete("/events/{event_id}")
def delete_event(event_id: int, session: SessionDep):
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with id {event_id} not found",
        )


    session.delete(event)
    session.commit()
    return {"message": "Event deleted"}