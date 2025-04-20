from flask import Blueprint, jsonify, request, current_app, render_template
import asyncio
from services.presentation import (
    send_presentation_request,
    fetch_credentials,
    send_presentation,
)
from config import VERIFIER_ADMIN_URL, HOLDER_ADMIN_URL

routes_bp = Blueprint("routes", __name__)

@routes_bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@routes_bp.route("/start_proof", methods=["POST"])
async def start_proof():
    try:
        # Assume send_presentation_request returns both pres_ex_id and thread_id
        result = await send_presentation_request(VERIFIER_ADMIN_URL)
        pres_ex_id = result["pres_ex_id"]
        thread_id = result["thread_id"]  # Adjust based on actual response

        if not hasattr(current_app, 'thread_to_verifier_pres_ex_id'):
            current_app.thread_to_verifier_pres_ex_id = {}
        current_app.thread_to_verifier_pres_ex_id[thread_id] = pres_ex_id

        return jsonify({"pres_ex_id": pres_ex_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_bp.route("/pending_presentations", methods=["GET"])
def get_pending_presentations():
    return jsonify(current_app.pending_presentations), 200

@routes_bp.route("/fetch_credentials/<pres_ex_id>", methods=["GET"])
async def fetch_creds(pres_ex_id):
    try:
        creds = await fetch_credentials(HOLDER_ADMIN_URL, pres_ex_id)
        return jsonify([
            {
                "cred_id": c["cred_info"]["referent"],
                "attrs": c["cred_info"]["attrs"]
            } for c in creds
        ]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_bp.route("/send_presentation", methods=["POST"])
async def submit_presentation():
    payload = request.get_json()
    holder_pres_ex_id = payload.get("pres_ex_id")  # Holder's pres_ex_id
    cred_id = payload.get("cred_id")
    if not (holder_pres_ex_id and cred_id):
        return jsonify({"error": "pres_ex_id and cred_id required"}), 400

    # Find the verifier's pres_ex_id using the mapping
    verifier_pres_ex_id = current_app.presentation_pairs.get(holder_pres_ex_id)
    if not verifier_pres_ex_id:
        return jsonify({"error": "No matching verifier pres_ex_id found"}), 500

    loop = asyncio.get_running_loop()
    event = asyncio.Event()
    current_app.verification_events[verifier_pres_ex_id] = {
        "event": event, "loop": loop, "result": None
    }

    try:
        await send_presentation(HOLDER_ADMIN_URL, holder_pres_ex_id, cred_id)
        await asyncio.wait_for(event.wait(), timeout=60)

        verified = current_app.verification_events[verifier_pres_ex_id]["result"]
        if verified:
            return jsonify({
                "message": "Access granted",
                "numbers": [1, 2, 3, 4, 5]
            }), 200
        else:
            return jsonify({"error": "Verification failed"}), 403

    except asyncio.TimeoutError:
        return jsonify({"error": "Verification timed out"}), 408

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        current_app.verification_events.pop(verifier_pres_ex_id, None)

def register_routes(app):
    app.register_blueprint(routes_bp)
