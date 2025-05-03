import jwt
from fastapi import Depends, HTTPException, status, WebSocket
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from jwt.exceptions import PyJWTError

from sqlmodel import Session, select

from app.database.database import get_session
from app.users.models import User
from settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    session: Session = Depends(get_session)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, 
            settings.secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception
    
    user = session.exec(select(User).where(User.id == user_id)).first()
    if user is None:
        raise credentials_exception
    
    return user


class WebSocketAuth:
    async def authenticate(self, websocket: WebSocket, session: Session) -> Optional[User]:
        try:
            token = websocket.query_params.get("token")
            print(f"Token({token})")
            if not token:
                return None
                
            payload = jwt.decode(
                token, 
                settings.secret_key,
                algorithms=[settings.jwt_algorithm]
            )
            user_id = payload.get("sub")
            if not user_id:
                return None
                
            user = session.exec(select(User).where(User.id == user_id)).first()
            return user
        except PyJWTError:
            return None

websocket_auth = WebSocketAuth()

