import pytest
from pydantic import ValidationError

from app.users.form import UserCreate, Token, UserLogin


class TestUserForms:
    def test_user_create_valid(self):
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepassword123"
        }
        user = UserCreate(**user_data)
        assert user.username == user_data["username"]
        assert user.email == user_data["email"]
        assert user.password == user_data["password"]

    def test_user_create_invalid_email(self):
        user_data = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "securepassword123"
        }
        with pytest.raises(ValidationError):
            UserCreate(**user_data)

    def test_user_create_missing_fields(self):
        user_data = {
            "username": "testuser",
            "email": "test@example.com"
        }
        with pytest.raises(ValidationError):
            UserCreate(**user_data)

    def test_token_valid(self):
        token_data = {
            "access_token": "some.jwt.token",
            "token_type": "bearer"
        }
        token = Token(**token_data)
        assert token.access_token == token_data["access_token"]
        assert token.token_type == token_data["token_type"]

    def test_user_login_valid(self):
        login_data = {
            "email": "test@example.com",
            "password": "securepassword123"
        }
        login = UserLogin(**login_data)
        assert login.email == login_data["email"]
        assert login.password == login_data["password"]

    def test_user_login_invalid_email(self):
        login_data = {
            "email": "invalid-email",
            "password": "securepassword123"
        }
        with pytest.raises(ValidationError):
            UserLogin(**login_data)
