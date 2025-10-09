from flask import Flask, request
import base64, json, os
from google.cloud import firestore
from shared import firestore_client, pubsub_client, schemas
from datetime import datetime

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

    # Forecast simple: media móvil dummy
    forecasts = {
        "Business": {"mu": 5, "sigma": 1.0},
        "Standard": {"mu": 20, "sigma": 4.0},
        "LowFare": {"mu": 50, "sigma": 8.0},
    }

    forecast_payload = {
        "departure_id": dep_id,
        "lead_time": "7d",
        "computed_at": datetime.utcnow().isoformat(),
        "forecasts": forecasts,
    }
    pubsub_client.publish(TOPICS["FORECAST"], forecast_payload)
    db.collection("forecasts").document(dep_id).set(forecast_payload)
    return ("", 204)

if __name__ == "__main__":
    app.run(port=8080)