from pydantic import BaseSettings

class Settings(BaseSettings):
    
    PROJECT_NAME: str = "DIDComm App"
    VERSION: str = "0.1.0"
    WEBHOOK_PORT: int = 5000
    
    
    ISSUER_AGENT_URL: str = "http://localhost:8061"
    HOLDER_AGENT_URL: str = "http://localhost:8062"
    VERIFIER_AGENT_URL: str = "http://localhost:8063"
    WEBHOOK_BASE_URL: str = "http://localhost:5000/webhooks/topic"
    
    REDIS_URL: str = "redis://localhost:6379/0"
    
    WEBHOOK_TOPICS: list = [
        "basicmessages",
        "issue_credential_v2_0",
        "present_proof_v2_0",
        "connections"
    ]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        
settings = Settings()