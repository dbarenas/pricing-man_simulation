from flask import Flask, request
import base64, json, os
from shared import firestore_client, pubsub_client, schemas
from datetime import datetime

app = Flask(__name__)
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

    fill_rate = event.get("fill_rate", 0)
    # regla simple
    factor = 1.0
    reason = "normal"
    if fill_rate < 0.5:
        factor = 0.9; reason = "ocupacion<50%"
    elif fill_rate > 0.8:
        factor = 1.1; reason = "ocupacion>80%"

    prices = {"LowFare": round(300 * factor, 2),
              "Standard": round(750 * factor, 2),
              "Business": round(900 * factor, 2)}

    sug = {
        "departure_id": dep_id,
        "timestamp": datetime.utcnow().isoformat(),
        "price_suggestions": prices,
        "reason": reason,
    }
    pubsub_client.publish(TOPICS["PRICE"], sug)
    return ("", 204)

if __name__ == "__main__":
    app.run(port=8080)