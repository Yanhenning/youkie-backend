import pytest
import jwt

from fastapi import WebSocket
from sqlmodel import Session

from app.users.models import User
from fastapi import HTTPException

from app.security.auth import get_current_user, websocket_auth
from settings import settings


@pytest.fixture
def mock_user():
    return User(id="test-user-id", username="testuser", email="test@example.com", hashed_password="hashed")


@pytest.fixture
def mock_session(mocker, mock_user):
    session = mocker.Mock(spec=Session)

    mock_exec = mocker.Mock()
    mock_exec.first.return_value = mock_user
    session.exec.return_value = mock_exec

    return session


@pytest.fixture
def valid_token(mock_user):
    return jwt.encode(
        {"sub": mock_user.id},
        settings.secret_key,
        algorithm=settings.jwt_algorithm
    )


@pytest.fixture
def invalid_token():
    return jwt.encode(
        {"sub": "non-existent-user"},
        "wrong-secret",
        algorithm=settings.jwt_algorithm
    )


@pytest.fixture
def mock_websocket(mocker):
    websocket = mocker.Mock(spec=WebSocket)
    websocket.query_params = {}
    return websocket


@pytest.mark.asyncio
async def test_get_current_user_valid_token(mock_session, valid_token, mock_user):
    user = await get_current_user(valid_token, mock_session)
    
    mock_session.exec.assert_called_once()
    
    assert user.id == mock_user.id
    assert user.username == mock_user.username


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(mock_session, invalid_token):
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(invalid_token, mock_session)
    
    assert exc_info.value.status_code == 401
    assert "Could not validate credentials" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_get_current_user_nonexistent_user(mock_session, valid_token, mocker):
    mock_exec = mocker.Mock()
    mock_exec.first.return_value = None
    mock_session.exec.return_value = mock_exec
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(valid_token, mock_session)
    
    assert exc_info.value.status_code == 401
    assert "Could not validate credentials" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_get_current_user_invalid_payload(mock_session):
    token = jwt.encode(
        {"not_sub": "something"},
        settings.secret_key,
        algorithm=settings.jwt_algorithm
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token, mock_session)
    
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_websocket_auth_valid_token(mock_session, valid_token, mock_user, mock_websocket):
    mock_websocket.query_params = {"token": valid_token}
    
    user = await websocket_auth.authenticate(mock_websocket, mock_session)
    
    assert user is not None
    assert user.id == mock_user.id


@pytest.mark.asyncio
async def test_websocket_auth_missing_token(mock_session, mock_websocket):
    mock_websocket.query_params = {}
    
    user = await websocket_auth.authenticate(mock_websocket, mock_session)
    
    assert user is None


@pytest.mark.asyncio
async def test_websocket_auth_invalid_token(mock_session, invalid_token, mock_websocket):
    mock_websocket.query_params = {"token": invalid_token}
    
    user = await websocket_auth.authenticate(mock_websocket, mock_session)
    
    assert user is None


@pytest.mark.asyncio
async def test_websocket_auth_nonexistent_user(mock_session, valid_token, mock_websocket, mocker):
    mock_exec = mocker.Mock()
    mock_exec.first.return_value = None
    mock_session.exec.return_value = mock_exec
    
    mock_websocket.query_params = {"token": valid_token}
    
    user = await websocket_auth.authenticate(mock_websocket, mock_session)
    
    assert user is None
