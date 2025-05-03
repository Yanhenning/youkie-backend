import pytest
from sqlmodel import Session

from app.users.models import User
from app.users.form import UserCreate
from app.users import service as user_service


@pytest.fixture
def mock_user():
    return User(
        id="test-id",
        username="testuser",
        email="test@example.com",
        password="$2b$12$testhashedpassword"
    )


@pytest.fixture
def mock_db(mocker, mock_user):
    db = mocker.Mock(spec=Session)
    
    # Configure mock query execution
    mock_exec = mocker.Mock()
    mock_exec.first.return_value = None  # Default to user not found
    db.exec.return_value = mock_exec
    
    return db


class TestUserService:
    def test_get_user_by_email_found(self, mock_db, mock_user, mocker):
        mock_exec = mocker.Mock()
        mock_exec.first.return_value = mock_user
        mock_db.exec.return_value = mock_exec
        
        user = user_service.get_user_by_email(mock_db, "test@example.com")
        
        assert user is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        mock_db.exec.assert_called_once()

    def test_get_user_by_email_not_found(self, mock_db):
        user = user_service.get_user_by_email(mock_db, "nonexistent@example.com")
        
        assert user is None
        mock_db.exec.assert_called_once()

    def test_get_user_by_username_found(self, mock_db, mock_user, mocker):
        mock_exec = mocker.Mock()
        mock_exec.first.return_value = mock_user
        mock_db.exec.return_value = mock_exec
        
        user = user_service.get_user_by_username(mock_db, "testuser")
        
        assert user is not None
        assert user.username == "testuser"
        mock_db.exec.assert_called_once()

    def test_get_user_by_username_not_found(self, mock_db):
        user = user_service.get_user_by_username(mock_db, "nonexistentuser")
        
        assert user is None
        mock_db.exec.assert_called_once()

    def test_create_user(self, mock_db, mocker):
        mocker.patch('app.users.service.get_password_hash', return_value="hashed_password")
        
        user_create = UserCreate(
            username="newuser",
            email="new@example.com",
            password="password123"
        )
        
        created_user = user_service.create_user(mock_db, user_create)
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        assert created_user is not None

    def test_authenticate_user_success(self, mock_db, mock_user, mocker):
        mocker.patch('app.users.service.get_user_by_email', return_value=mock_user)
        mocker.patch('app.users.service.verify_password', return_value=True)
        
        authenticated = user_service.authenticate_user(mock_db, "test@example.com", "password123")
        
        assert authenticated is not None
        assert authenticated.email == "test@example.com"

    def test_authenticate_user_wrong_password(self, mock_db, mock_user, mocker):
        mocker.patch('app.users.service.get_user_by_email', return_value=mock_user)
        mocker.patch('app.users.service.verify_password', return_value=False)
        
        authenticated = user_service.authenticate_user(mock_db, "test@example.com", "wrongpassword")
        
        assert authenticated is False

    def test_authenticate_user_not_found(self, mock_db, mocker):
        mocker.patch('app.users.service.get_user_by_email', return_value=None)
        
        authenticated = user_service.authenticate_user(mock_db, "nonexistent@example.com", "password123")
        
        assert authenticated is False
