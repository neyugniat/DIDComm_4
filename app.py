import os
from flask import Flask
from webhooks import register_webhooks
from routes import register_routes
from config import HOST, PORT

def create_app():
    app = Flask(__name__)
    app.verification_events = {}
    register_webhooks(app)
    register_routes(app)
    return app

if __name__ == "__main__":
    from hypercorn.asyncio import serve
    from hypercorn.config import Config
    import asyncio

    app = create_app()
    config = Config()
    config.bind = [f"{HOST}:{PORT}"]
    asyncio.run(serve(app, config))