
# Youkie Backend

A FastAPI-based backend service with SQLModel, JWT authentication, and LangChain integration.

## Project Overview

Youkie Backend provides:
- User authentication and management
- Real-time AI conversations via WebSockets
- Integration with language models through LangChain

## Setup Instructions

### Prerequisites
- Python 3.8+
- pip
- Make (optional, for convenience commands)

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with the following variables or using the .env-sample file:
   ```
   DATABASE_URL=sqlite:///./youkie.db
   SECRET_KEY=your_secure_secret_key
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   OPENAI_API_KEY=your_openai_api_key_here
   JWT_ALGORITHM
   ```

### Running the Application
You can run the application in two ways:
- Using Docker (recommended for production)
- Locally with Python

Start the application using docker:
```bash
make run
```

Or running locally with a virtualenv and fastapi:
```bash
fastapi run main.py
```

This executes the FastAPI application with hot-reloading enabled for development.

## Technical Implementation

### Database
- SQLModel for ORM capabilities, combining SQLAlchemy Core and Pydantic
- Automatic table creation at application startup
- Efficient data validation and type safety
#### Improvements:
- Currently using SQLite for simplicity, but can be configured for other databases such as MySQL or PostgreSQL

### Authentication
- JWT-based authentication using PyJWT
- Secure password hashing
- Token-based session management
#### Improvements:
- Implement refresh tokens for better session management
- Add throttling in the application or API gateway to prevent abuse
- Implement user roles and permissions for more granular access control

### WebSocket Implementation
WebSockets provide real-time, bidirectional communication channels between clients and the server:
- Persistent connections for immediate response delivery
- Reduced overhead compared to HTTP polling
- Efficient handling of streaming responses from language models
- Authentication and authorization for secure connections

### LangChain Integration creating a LLM service

By using the LangChain library, I can easily integrate different language models into the application.
So this way I can create a service that can be used to create a LLM service for different models such as OpenAI, Cohere, and others.
The way I built my service I can easily extend it to support other models in the future or change it to use a different model.

In other words the LangChain helps me with:
- Contextual conversation chains maintain state between messages
- Abstract interface to various language models
- Advanced prompting techniques and conversation memory
- Processing and structuring of AI responses

## API Documentation
Once running, access the interactive API documentation at:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)
