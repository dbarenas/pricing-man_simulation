from flask import Flask, request
from google.cloud import firestore
import base64, json, os
from shared import firestore_client, pubsub_client, schemas

app = Flask(__name__)
db = firestore_client.get_db()
PROJECT_ID = os.environ.get("GCP_PROJECT")
TOPICS = schemas.default_topics(PROJECT_ID)

@app.route("/pubsub/push", methods=["POST"])
def pubsub_push():
    envelope = request.get_json()
    if not envelope or "message" not in envelope:
        return ("Bad Request", 400)
    data_b64 = envelope["message"].get("data", "")
    event = json.loads(base64.b64decode(data_b64).decode("utf-8"))

    dep_id = event["departure_id"]
    doc_ref = db.collection("departures").document(dep_id)
    res_ref = doc_ref.collection("reservations").document(event["reservation_id"])

    res_ref.set(event)

    doc = doc_ref.get()
    doc_data = doc.to_dict() if doc.exists else {}

    lane_reserved = doc_data.get("reserved_lane_m", 0)
    total_lane_m = doc_data.get("total_lane_m", 1) # Avoid division by zero

    lane_reserved += event["vehicle"].get("length_m", 4.0)

    doc_ref.set({"reserved_lane_m": lane_reserved}, merge=True)

    fill_rate = min(lane_reserved / total_lane_m, 1.0)

    occ_update = {"departure_id": dep_id, "fill_rate": fill_rate, "reserved_lane_m": lane_reserved}
    pubsub_client.publish(TOPICS["OCCUPATION"], occ_update)
    return ("", 204)

if __name__ == "__main__":
    app.run(port=8080)