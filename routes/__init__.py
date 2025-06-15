from fastapi import FastAPI

from routes.connections import router as connections_router
from routes.basicmessages import router as basicmessages_router
from routes.websocket_messages import router as websocket_router
from routes.credential_definitions import router as credential_definitions_router
from routes.schemas import router as schemas_router
from routes.issue_credentials import router as issue_credentials_router
from routes.wallet import router as wallet_router
from routes.presentations import router as presentations_router
from routes.jwt_credentials import router as jwt_credentials_router
from routes.api_system import router as api_system_router
from routes.jwt_wallet import router as jwt_wallet_router
from routes.age_presentation import router as age_presentation_router
from routes.credentials import router as credentials_router
from routes.graduated_presentation import router as graduated_presentaions_router
from routes.did import router as did_router
from routes.manual_presentations import router as manual_presentations_router
from routes.revocation import router as revocation_router

def register_routes(app: FastAPI):
    app.include_router(connections_router, prefix="/connections", tags=["Connections"])
    app.include_router(basicmessages_router, prefix="/basicmessages", tags=["Basic Messages"])
    app.include_router(websocket_router, prefix="/chat", tags=["Chat"])
    app.include_router(credential_definitions_router, prefix="/credential-definitions", tags=["Credential Definitions"])
    app.include_router(schemas_router, prefix="/schemas", tags=["Schemas"])
    app.include_router(issue_credentials_router, prefix="/issue-credentials", tags=["Issue Credentials"])
    app.include_router(wallet_router, prefix="/wallet", tags=["Wallet"])
    app.include_router(presentations_router, prefix="/presentations", tags=["Presentations"])
    app.include_router(jwt_credentials_router, prefix="/jwt-credentials", tags=["JWT Credentials"])
    app.include_router(api_system_router, prefix="/api", tags=["API System"])
    app.include_router(jwt_wallet_router, prefix="/jwt-wallet", tags=["JWT Wallet"])
    app.include_router(age_presentation_router, prefix="/age_presentation", tags=["Age Presentation"])
    app.include_router(credentials_router, prefix="/credentials", tags=["Credentials"])
    app.include_router(graduated_presentaions_router, prefix="/graduated_presentation", tags=["Graduated Presentation"])
    app.include_router(did_router, prefix="/did", tags=["DID"])
    app.include_router(manual_presentations_router, prefix="/manual_presentations", tags=["Manual Presentations"])
    app.include_router(revocation_router, prefix="/revocation", tags=["Revocation"])