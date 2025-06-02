from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.basicmessages import send_message
import logging

router = APIRouter()
logger = logging.getLogger("routes.basicmessages")

class MessageRequest(BaseModel):
    agent_type: str
    connection_id: str
    content: str

@router.post("/send_message")
async def send_basic_message(message: MessageRequest):
    try:
        result = await send_message(message.agent_type, message.connection_id, message.content)
        return {"message": "Message sent", **result}
    except Exception as e:
        logger.error(f"Failed to send message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))