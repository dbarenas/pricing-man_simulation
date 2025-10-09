import os
import json
import time
import uuid
import random
from datetime import datetime, timedelta
from google.cloud import pubsub_v1

# Configuración inicial
PROJECT_ID = os.environ.get("GCP_PROJECT")
if not PROJECT_ID:
    raise ValueError("El environment variable GCP_PROJECT es obligatorio")
TOPIC_ID = os.environ.get("TOPIC_RESERVAS", "reservas")
TOPIC_PATH = f"projects/{PROJECT_ID}/topics/{TOPIC_ID}"

# Instancia Publisher
publisher = pubsub_v1.PublisherClient()

# --- Configuración de Departures de prueba ---
DEPARTURES = [
    {
        "departure_id": "PALMA-IBIZA-2025-07-01-09:30",
        "route": "Palma-Ibiza",
        "total_lane_m": 1200,
        "avg_vehicle_m": 4.5,
        "base_prices": {"LowFare": 300, "Standard": 750, "Business": 900}
    },
    {
        "departure_id": "IBIZA-PALMA-2025-07-01-18:00",
        "route": "Ibiza-Palma",
        "total_lane_m": 1200,
        "avg_vehicle_m": 4.5,
        "base_prices": {"LowFare": 290, "Standard": 740, "Business": 890}
    }
]

# --- Parámetros de simulación ---
SCENARIO = os.environ.get("SCENARIO", "medium")  # low | medium | high
INTERVAL_SECONDS = float(os.environ.get("INTERVAL_SECONDS", 2.0))
BATCH_SIZE = int(os.environ.get("BATCH_SIZE", 5))  # reservas por lote
RANDOM_SEED = 42

random.seed(RANDOM_SEED)

def random_vehicle():
    """Genera vehículo aleatorio con longitud aproximada."""
    types = [
        ("car", 4.3),
        ("van", 5.5),
        ("moto", 2.2),
        ("truck_small", 7.0)
    ]
    return dict(zip(["type", "length_m"], random.choice(types)))

def passengers_by_vehicle(vtype):
    return {
        "car": random.randint(1, 4),
        "van": random.randint(2, 6),
        "moto": random.randint(1, 2),
        "truck_small": random.randint(1, 2)
    }.get(vtype, 1)

def reservations_to_send(departure):
    """Decide cantidad de reservas según escenario."""
    if SCENARIO == "low":
        return random.randint(5, 10)
    if SCENARIO == "medium":
        return random.randint(15, 30)
    if SCENARIO == "high":
        return random.randint(40, 60)
    return 20

def build_reservation_event(dep):
    """Construye un evento de reserva aleatorio."""
    veh = random_vehicle()
    passengers = passengers_by_vehicle(veh["type"])
    return {
        "type": "reservation.created",
        "departure_id": dep["departure_id"],
        "reservation_id": f"RES-{uuid.uuid4()}",
        "timestamp": datetime.utcnow().isoformat(),
        "passengers": passengers,
        "vehicle": veh,
        "fare_class": random.choices(
            ["LowFare", "Standard", "Business"], weights=[0.6, 0.3, 0.1]
        )[0],
    }

def publish_reservation(event):
    """Publica evento JSON a Pub/Sub."""
    data = json.dumps(event).encode("utf-8")
    future = publisher.publish(TOPIC_PATH, data=data)
    future.result()  # bloquea hasta confirmar envío
    print(f"[{datetime.utcnow().isoformat()}] → Published {event['reservation_id']} to {event['departure_id']}")

def run_simulation():
    print(f"\n🚀 Iniciando simulación de reservas ({SCENARIO.upper()} load)")
    print(f"Publicando en topic: {TOPIC_PATH}")
    for dep in DEPARTURES:
        n_res = reservations_to_send(dep)
        print(f"\n➡️  Departure {dep['departure_id']} — enviando {n_res} reservas")
        for _ in range(n_res):
            event = build_reservation_event(dep)
            publish_reservation(event)
            time.sleep(INTERVAL_SECONDS)
    print("\n✅ Simulación completa.\n")

if __name__ == "__main__":
    run_simulation()