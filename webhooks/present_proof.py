from flask import jsonify, current_app

def handle_proof_presentation(event):
    verification_events = current_app.verification_events
    role = event.get("role")
    state = event.get("state")
    pres_ex_id = event.get("pres_ex_id")

    print(f"Role: {role}, state: {state}")

    is_verified = False

    if role == "verifier":
        if state == "done":
            verified_flag = event.get("verified")
            if verified_flag == "true":
                is_verified = True
                print(f"✅ User verified successfully: pres_ex_id: {pres_ex_id}")
            else:
                print("❌ Verification failed!!!")
            if pres_ex_id in verification_events:
                verification_events[pres_ex_id]["result"] = is_verified
                loop = verification_events[pres_ex_id]["loop"]
                loop.call_soon_threadsafe(verification_events[pres_ex_id]["event"].set)
                print(f"Event set immediately for pres_ex_id: {pres_ex_id}")
            else:
                print(f"pres_ex_id {pres_ex_id} not found in verification_events!")
        elif state == "request-sent":
            pass
        elif state == "presentation-received":
            pass
        elif state == "deleted":
            pass
        else:
            pass
    else:
        pass

    return jsonify({"verified": is_verified}), 200
