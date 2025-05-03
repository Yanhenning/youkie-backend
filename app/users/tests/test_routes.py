import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.users.models import User
from main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_user():
    return User(
        id="test-id",
        username="testuser",
        email="test@example.com",
        password="hashed_password"
    )


@pytest.fixture
def mock_token():
    return "mock.jwt.token"


class TestAuthRoutes:
    def test_register_user_success(self, client, mocker):
        mocker.patch('app.users.service.get_user_by_email', return_value=None)
        mocker.patch('app.users.service.get_user_by_username', return_value=None)
        
        mock_created_user = User(id="new-id", username="newuser", email="new@example.com", password="hashed")
        mocker.patch('app.users.service.create_user', return_value=mock_created_user)
        mocker.patch('app.users.routes.create_access_token', return_value="mock.token")
        
        response = client.post(
            "/auth/register",
            json={
                "username": "newuser",
                "email": "new@example.com",
                "password": "securepassword123"
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "user" in data
        assert "access_token" in data
        assert data["user"]["username"] == "newuser"
        assert data["access_token"] == "mock.token"

    def test_register_user_email_exists(self, client, mock_user, mocker):
        mocker.patch('app.users.service.get_user_by_email', return_value=mock_user)
        
        response = client.post(
            "/auth/register",
            json={
                "username": "newuser",
                "email": "test@example.com",
                "password": "securepassword123"
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Email already registered" in response.json()["detail"]

    def test_register_user_username_exists(self, client, mock_user, mocker):
        mocker.patch('app.users.service.get_user_by_email', return_value=None)
        mocker.patch('app.users.service.get_user_by_username', return_value=mock_user)
        
        response = client.post(
            "/auth/register",
            json={
                "username": "testuser",
                "email": "new@example.com",
                "password": "securepassword123"
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Username already taken" in response.json()["detail"]

    def test_login_successful(self, client, mock_user, mocker):
        mocker.patch('app.users.service.authenticate_user', return_value=mock_user)
        mocker.patch('app.users.routes.create_access_token', return_value="mock.token")
        
        response = client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "securepassword123"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["access_token"] == "mock.token"
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client, mocker):
        mocker.patch('app.users.service.authenticate_user', return_value=False)
        
        response = client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect email or password" in response.json()["detail"]
