from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from datetime import timedelta

from app.users.form import UserCreate, Token, UserLogin
from app.database.database import get_db
from app.users import service as user_crud
from app.users.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)

@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = user_crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    username_exists = user_crud.get_user_by_username(db, username=user.username)
    if username_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    created_user = user_crud.create_user(db=db, user=user)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(created_user.id)}, expires_delta=access_token_expires
    )

    return {
        "user": created_user,
        "access_token": access_token,
        "token_type": "bearer"
    }


@auth_router.post("/login", response_model=Token)
def login_with_email(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    user = user_crud.authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
