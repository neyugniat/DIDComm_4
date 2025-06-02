import httpx
from config import settings
import logging

logger = logging.getLogger("agent_service")

async def send_message(agent_type: str, connection_id: str, content: str):
    """Send a basic message via Aries agent."""
    agent_urls = {
        "issuer": settings.ISSUER_AGENT_URL,
        "holder": settings.HOLDER_AGENT_URL,
        "verifier": settings.VERIFIER_AGENT_URL
    }
    if agent_type not in agent_urls:
        logger.error(f"Invalid agent type: {agent_type}")
        raise ValueError(f"Invalid agent type: {agent_type}")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{agent_urls[agent_type]}/connections/{connection_id}/send-message",
            json={"content": content},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code != 200:
            logger.error(f"Failed to send message: {response.text}")
            raise RuntimeError(f"Failed to send message: {response.text}")
        data = response.json()
        return {
            "status": "success",
            "message_id": data.get("message_id", "unknown")
        }