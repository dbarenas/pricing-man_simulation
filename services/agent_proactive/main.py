from flask import Flask, request
import base64, json, os
from shared import firestore_client, schemas
from datetime import datetime

app = Flask(__name__)
db = firestore_client.get_db()
PROJECT_ID = os.environ.get("GCP_PROJECT")

@app.route("/pubsub/push", methods=["POST"])
def pubsub_push():
    envelope = request.get_json()
    if not envelope or "message" not in envelope:
        return ("Bad Request", 400)
    data_b64 = envelope["message"].get("data", "")
    event = json.loads(base64.b64decode(data_b64).decode("utf-8"))

    action = {
        "departure_id": event["departure_id"],
        "timestamp": datetime.utcnow().isoformat(),
        "action_type": "PROMOTION" if "ocupacion<50%" in event.get("reason","") else "NORMAL",
        "details": event,
    }
    db.collection("actions_promotions").add(action)
    print(f"Action logged for {event['departure_id']}")
    return ("", 204)

if __name__ == "__main__":
    app.run(port=8080)