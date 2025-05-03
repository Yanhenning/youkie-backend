import logging

from fastapi import APIRouter, Depends, status
from fastapi import HTTPException
from starlette.responses import StreamingResponse
from starlette.websockets import WebSocket
import json
from sqlmodel import Session

from app.database.database import get_session
from app.enums import SummarizationStyle
from app.services.llm_service import LlmService
from app.security.auth import get_current_user, websocket_auth
from app.users.models import User

active_connections = {}

router = APIRouter(
    prefix="/api",
    tags=["api"],
    responses={404: {"description": "Not found"}},
)

log = logging.getLogger(__name__)


@router.get("/health")
async def health_check():
    return {"status": "healthy"}


@router.get("/test")
async def test_endpoint(current_user: User = Depends(get_current_user)):
    return {
        "message": "Your endpoint is authenticated",
        "user_id": current_user.id,
        "email": current_user.email
    }


@router.get("/stream_summarize_text")
async def stream_summarize_text(
    content: str,
    style: SummarizationStyle = SummarizationStyle.NORMAL,
    current_user: User = Depends(get_current_user)
):
    try:
        service = LlmService(streaming=True)
        response = StreamingResponse(
            service.summarize_blog_post_stream(content, style=style.value), media_type="text/plain"
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to summarize text via streaming: {str(e)}")

@router.websocket("/ws/summarize_stream")
async def websocket_summarize_stream(websocket: WebSocket, session: Session = Depends(get_session)):
    user = await websocket_auth.authenticate(websocket, session)
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()

    connection_id = id(websocket)
    service = LlmService(streaming=True)
    active_connections[connection_id] = {"websocket": websocket, "service": service, "user": user}

    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                content = message.get("text", "")
                style = message.get("style", SummarizationStyle.BULLET_POINTS.value)

                text = service.summarize_blog_post_stream(content, style)
                await websocket.send_text(text)

            except json.JSONDecodeError:
                await websocket.send_text("Error: Invalid JSON format")
            except Exception as e:
                await websocket.send_text(f"Error: {str(e)}")
    except Exception as e:
        pass
    finally:
        if connection_id in active_connections:
            del active_connections[connection_id]
