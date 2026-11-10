import os
from dotenv import load_dotenv
from requests import session
from sqlmodel import SQLModel, Session, create_engine

load_dotenv()
engine = create_engine(os.environ["DATABASE_URL"], echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
def get_session():
    with Session(engine) as session:
        yield session