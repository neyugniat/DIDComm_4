from flask import Blueprint, jsonify, current_app, render_template
import asyncio
from services.presentation import send_presentation_request
from config import VERIFIER_ADMIN_URL

routes_bp = Blueprint("routes", __name__)

@routes_bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@routes_bp.route("/get_number_list", methods=["POST"])
async def get_number_list():
    try:
        pres_ex_id = await send_presentation_request(VERIFIER_ADMIN_URL)
    except RuntimeError as err:
        return jsonify({"error": str(err)}), 500

    loop = asyncio.get_running_loop()
    event = asyncio.Event()
    current_app.verification_events[pres_ex_id] = {"event": event, "loop": loop, "result": None}

    try:
        await asyncio.wait_for(event.wait(), timeout=60)
        verified = current_app.verification_events[pres_ex_id]["result"]
        if verified:
            return jsonify({"message": "Access granted", "numbers": [1, 2, 3, 4, 5]}), 200
        return jsonify({"error": "Verification failed"}), 403
    except asyncio.TimeoutError:
        return jsonify({"error": "Verification timed out"}), 408
    finally:
        current_app.verification_events.pop(pres_ex_id, None)

def register_routes(app):
    app.register_blueprint(routes_bp)