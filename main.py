from fastapi import FastAPI
from app.routes import router

# Create FastAPI app
app = FastAPI(
    title="Youkie API",
    description="Youkie AI your friendly assistant",
    version="0.1.0",
)

# Include the router
app.include_router(router)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI application"}
