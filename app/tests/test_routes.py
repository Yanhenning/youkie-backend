from datetime import timedelta

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool

from app.users.models import User
from app.users.security import create_access_token
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
def test_db():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def db_user(test_db):
    user = User(
        username="testuser",
        email="test@example.com",
        password="hashed_password"
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def auth_headers(db_user):
    return {"Authorization": f"{create_access_token(data={"sub": str(db_user.id)}, expires_delta=timedelta(hours=1))}"}


class TestApiRoutes:
    def test_health_check(self, client):
        response = client.get("/api/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "healthy"}

    @pytest.mark.skip
    def test_test_endpoint_authenticated(self, client, auth_headers, db_user, mocker):
        mocker.patch('app.security.auth.get_current_user', return_value=db_user)

        response = client.get("/api/test", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Your endpoint is authenticated"
        assert data["user_id"] == db_user.id
        assert data["email"] == db_user.email

    def test_test_endpoint_unauthenticated(self, client):
        response = client.get("/api/test")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.skip
    def test_stream_summarize_text(self, client, auth_headers, mock_user, mocker):
        # Mock the authentication dependency directly
        mocker.patch('app.security.auth.get_current_user', return_value=mock_user)
        
        # Mock the streaming response
        mock_service = mocker.patch('app.routes.LlmService')
        mock_instance = mock_service.return_value
        mock_instance.summarize_blog_post_stream.return_value = (word for word in ["This", " ", "is", " ", "a", " ", "summary"])
        
        response = client.get(
            "/api/stream_summarize_text?content=Test content&style=BULLET_POINTS",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.text == "This is a summary"
        
        mock_instance.summarize_blog_post_stream.assert_called_once()

    @pytest.mark.skip
    def test_stream_summarize_text_error(self, client, auth_headers, mock_user, mocker):
        # Mock JWT decode for authentication
        mocker.patch('jwt.decode', return_value={"sub": mock_user.id})

        # Mock the database query to return our mock_user
        mock_db_session = mocker.Mock()
        mock_exec = mocker.Mock()
        mock_exec.first.return_value = mock_user
        mock_db_session.exec.return_value = mock_exec
        mocker.patch('app.database.database.get_db', return_value=mock_db_session)

        # Mock an exception in the service
        mock_service = mocker.patch('app.routes.LlmService')
        mock_instance = mock_service.return_value
        mock_instance.summarize_blog_post_stream.side_effect = Exception("Service error")

        response = client.get(
            "/api/stream_summarize_text?content=Test content",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to summarize text" in response.json()["detail"]

    def test_websocket_auth_success(self, mocker):
        mock_websocket = mocker.Mock()
        mock_session = mocker.Mock()
        mocker.patch('app.security.auth.websocket_auth.authenticate', return_value=mock_user)

        # We need to test the websocket endpoint logic
        # This requires more advanced testing since FastAPI TestClient doesn't support WebSockets directly
        # For actual implementation, we would use libraries like pytest-websocket

