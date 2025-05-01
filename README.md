
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

3. Create a `.env` file in the project root with the following variables:
   ```
   DATABASE_URL=sqlite:///./youkie.db
   SECRET_KEY=your_secure_secret_key
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   OPENAI_API_KEY=your_openai_api_key_here
   ```

### Running the Application

Start the application using docker:
```bash
make run
```

Or fastpi:
```bash
fastapi run main.py
```


This executes the FastAPI application with hot-reloading enabled for development.

## Technical Implementation

### Database
- SQLModel for ORM capabilities, combining SQLAlchemy Core and Pydantic
- Automatic table creation at application startup
- Efficient data validation and type safety

### Authentication
- JWT-based authentication using PyJWT
- Secure password hashing
- Token-based session management

### WebSocket Implementation
WebSockets provide real-time, bidirectional communication channels between clients and the server:
- Persistent connections for immediate response delivery
- Reduced overhead compared to HTTP polling
- Efficient handling of streaming responses from language models

### LangChain Integration
LangChain enhances the AI capabilities of the application:
- Contextual conversation chains maintain state between messages
- Abstract interface to various language models
- Advanced prompting techniques and conversation memory
- Processing and structuring of AI responses

## API Documentation
Once running, access the interactive API documentation at:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)
