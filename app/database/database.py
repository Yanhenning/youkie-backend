from sqlmodel import create_engine, Session, SQLModel

from settings import settings

engine = create_engine(
    settings.sqlalchemy_database_url, connect_args={"check_same_thread": False}
)

def get_db():
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session