from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import create_db_and_tables
from app.routes import router
from app.users.routes import auth_router


@asynccontextmanager
async def lifespan(app):
    create_db_and_tables()
    yield

app = FastAPI(
    title="Youkie API",
    description="Youkie AI your friendly assistant",
    version="0.1.0",
    lifespan=lifespan
)

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "ws://localhost",
    "ws://localhost:3000",
    "ws://localhost:8000",
    "ws://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(auth_router)

@app.get("/")
async def root():
    return {"message": "Welcome to Youkie API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
