from flask import Blueprint, request
from .present_proof import handle_proof_presentation

webhooks_bp = Blueprint('webhooks', __name__)

HANDLERS = {
    'present_proof_v2_0': handle_proof_presentation,
}

@webhooks_bp.route('/webhooks/topic/<string:topic>/', methods=['POST'])
def handle_webhook(topic):
    event = request.json
    print(f"Received event for topic: {topic}")

    handler = HANDLERS.get(topic)
    if handler:
        try:
            return handler(event)
        except Exception as e:
            print(f"Error handling {topic}: {e}")
            return "Internal server error", 500
    else:
        print(f"Unhandled topic: {topic}")
        return "Unhandled topic", 400

def register_webhooks(app):
    app.register_blueprint(webhooks_bp)