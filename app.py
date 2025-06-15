import logging

# Libraries
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager
import aioredis
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from config import settings
from routes import register_routes

# Webhooks
from webhooks.basicmessages import router as basicmessages_router
from webhooks.issue_credential_v2_0 import router as issue_credential_v2_0_router
from webhooks.present_proof_v2_0 import router as present_proof_v2_0_router
from webhooks.connections import router as connections_router
from webhooks.issue_credential_v2_0_indy import router as issue_credential_v2_0_indy_router
from webhooks.revocation_registry import router as revocation_registry_router
from webhooks.issuer_cred_rev import router as issuer_cred_rev_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Redis connection
    redis = await aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    app.state.redis = redis
    logger.info("Redis connected")
    yield
    # Shutdown: Close Redis connection
    await redis.close()
    logger.info("Redis disconnected")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory="static"), name="static")

register_routes(app)

app.include_router(basicmessages_router, prefix="/webhooks/topic/basicmessages")
app.include_router(issue_credential_v2_0_router, prefix="/webhooks/topic/issue_credential_v2_0")
app.include_router(present_proof_v2_0_router, prefix="/webhooks/topic/present_proof_v2_0")
app.include_router(connections_router, prefix="/webhooks/topic/connections")
app.include_router(issue_credential_v2_0_indy_router, prefix="/webhooks/topic/issue_credential_v2_0_indy")
app.include_router(revocation_registry_router, prefix="/webhooks/topic/revocation_registry")
app.include_router(issuer_cred_rev_router, prefix=("/webhooks/topic/issuer_cred_rev"))

@app.get("/")
async def root():
    with open("static/index.html") as f:
        return HTMLResponse(content=f.read())

@app.get("/issuer_connecting", response_class=HTMLResponse)
async def get_connections():
    with open("static/issuer_connecting.html") as f:
        return HTMLResponse(content=f.read())
    
@app.get("/schemas", response_class=HTMLResponse)
async def get_connections():
    with open("static/schemas.html") as f:
        return HTMLResponse(content=f.read())
    credential_definitions

@app.get("/credential_definitions", response_class=HTMLResponse)
async def get_connections():
    with open("static/credential_definitions.html") as f:
        return HTMLResponse(content=f.read())  
    
@app.get("/revocation", response_class=HTMLResponse)
async def get_connections():
    with open("static/revocation.html") as f:
        return HTMLResponse(content=f.read())  

@app.get("/verifier_connecting", response_class=HTMLResponse)
async def get_connections():
    with open("static/verifier_connecting.html") as f:
        return HTMLResponse(content=f.read())
    
@app.get("/connections/holder/display", response_class=HTMLResponse)
async def get_holder_connections():
    with open("static/holder_connections.html") as f:
        return HTMLResponse(content=f.read())

@app.get("/messenger", response_class=HTMLResponse)
async def get_messenger():
    with open("static/messenger.html") as f:
        return HTMLResponse(content=f.read())

@app.get("/messenger/{connection_id}", response_class=HTMLResponse)
async def get_messenger_connection(connection_id: str):
    with open("static/messenger.html") as f:
        return HTMLResponse(content=f.read())
    
@app.get("/credentials", response_class=HTMLResponse)
async def get_credentials():
    with open("static/credentials.html") as f:
        return HTMLResponse(content=f.read())
    
@app.get("/credential/{referent}", response_class=HTMLResponse)
async def get_credential_details(referent: str):
    with open("static/credential_details.html") as f:
        return HTMLResponse(content=f.read())

@app.get("/presentations", response_class=HTMLResponse)
async def get_presentations():
    with open("static/presentations.html") as f:
        return HTMLResponse(content=f.read())

@app.get("/manual_presentations", response_class=HTMLResponse)
async def get_presentations():
    with open("static/manual_presentations.html") as f:
        return HTMLResponse(content=f.read())   
    
@app.get("/jwt_credentials", response_class=HTMLResponse)
async def get_jwt_credentials():
    with open("static/jwt_credentials.html") as f:
        return HTMLResponse(content=f.read())
    
@app.get("/jwt_wallet", response_class=HTMLResponse)
async def get_jwt_wallet():
    with open("static/jwt_wallet.html") as f:
        return HTMLResponse(content=f.read())

@app.get("/api_test", response_class=HTMLResponse)
async def get_api_test():
    with open("static/api_test.html") as f:
        return HTMLResponse(content=f.read())

@app.get("/issuer/issue_credential", response_class=HTMLResponse)
async def get_issue_credential():
    with open("static/issuer_issue_credentials.html") as f:
        return HTMLResponse(content=f.read())

@app.get("/verifier/age_presentation", response_class=HTMLResponse)
async def get_issue_credential():
    with open("static/age_presentation.html") as f:
        return HTMLResponse(content=f.read())
    
@app.get("/verifier/graduated_presentation", response_class=HTMLResponse)
async def get_issue_credential():
    with open("static/graduated_presentation.html") as f:
        return HTMLResponse(content=f.read())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=settings.WEBHOOK_PORT, reload=True)

