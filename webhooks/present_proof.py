from flask import jsonify, current_app

def handle_proof_presentation(event):
    verification_events = current_app.verification_events
    
    if not hasattr(current_app, 'pending_presentations'):
        current_app.pending_presentations = []
    pending_presentations = current_app.pending_presentations
    
    if not hasattr(current_app, 'presentation_pairs'):
        current_app.presentation_pairs = {}  # Maps holder's to verifier's pres_ex_id
    if not hasattr(current_app, 'thread_to_verifier_pres_ex_id'):
        current_app.thread_to_verifier_pres_ex_id = {}

    role = event.get("role")
    state = event.get("state")
    pres_ex_id = event.get("pres_ex_id")
    thread_id = event.get("thread_id")  # Aries events include thread_id

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
    elif role == "prover":
        if state == "request-received":
            if pres_ex_id not in pending_presentations:
                pending_presentations.append(pres_ex_id)
                verifier_pres_ex_id = current_app.thread_to_verifier_pres_ex_id.get(thread_id)
                if verifier_pres_ex_id:
                    current_app.presentation_pairs[pres_ex_id] = verifier_pres_ex_id
                    print(f"Mapped holder pres_ex_id {pres_ex_id} to verifier pres_ex_id {verifier_pres_ex_id}")
                print(f"Added pres_ex_id {pres_ex_id} to pending_presentations")
        elif state == "presentation-sent":
            if pres_ex_id in pending_presentations:
                pending_presentations.remove(pres_ex_id)
                print(f"Removed pres_ex_id {pres_ex_id} from pending_presentations")
    else:
        pass

    return jsonify({"verified": is_verified}), 200