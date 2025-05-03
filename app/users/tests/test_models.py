import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool

from app.users.models import User


@pytest.fixture
def in_memory_db():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


class TestUserModel:
    def test_create_user(self, in_memory_db):
        user = User(
            username="testuser",
            email="test@example.com",
            password="hashedpassword"
        )
        in_memory_db.add(user)
        in_memory_db.commit()
        
        saved_user = in_memory_db.get(User, user.id)
        assert saved_user is not None
        assert saved_user.username == "testuser"
        assert saved_user.email == "test@example.com"
        assert saved_user.password == "hashedpassword"
        assert saved_user.id is not None

    def test_unique_email_constraint(self, in_memory_db):
        user1 = User(
            username="user1",
            email="same@example.com",
            password="hashedpassword1"
        )
        in_memory_db.add(user1)
        in_memory_db.commit()
        
        user2 = User(
            username="user2",
            email="same@example.com",
            password="hashedpassword2"
        )
        in_memory_db.add(user2)
        
        with pytest.raises(Exception):
            in_memory_db.commit()
        in_memory_db.rollback()

    def test_unique_username_constraint(self, in_memory_db):
        user1 = User(
            username="sameusername",
            email="user1@example.com",
            password="hashedpassword1"
        )
        in_memory_db.add(user1)
        in_memory_db.commit()
        
        user2 = User(
            username="sameusername",
            email="user2@example.com",
            password="hashedpassword2"
        )
        in_memory_db.add(user2)
        
        with pytest.raises(Exception):
            in_memory_db.commit()
        in_memory_db.rollback()
