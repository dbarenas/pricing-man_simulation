import datetime
from src.event_bus.memory_bus import MemoryEventBus
from src.agents.pricing_agent import PricingAgent
from src.models.events import DemandForecastEvent

def main():
    """
    Main function to run the simulation.
    """
    print("--- Ferry Seat Occupancy Simulation ---")

    # 1. Initialize the event bus
    event_bus = MemoryEventBus()

    # 2. Initialize agents
    pricing_agent = PricingAgent("pricing_agent_v1", event_bus)

    # 3. Agents subscribe to events
    pricing_agent.run()

    # 4. Add a handler to listen for the final price suggestion
    def price_suggestion_handler(event):
        print(f"[Simulation] Received final price suggestion: ${event.suggested_price} for trip {event.trip_id}")

    event_bus.subscribe("price_suggestion.v1", price_suggestion_handler)

    # 5. Simulate a demand forecast event
    print("\n--- Simulating a high-demand scenario ---")
    high_demand_forecast = DemandForecastEvent(
        trip_id="trip_2025_09_30_1800",
        forecast_time=datetime.datetime.now().isoformat(),
        horizon_hours=72,
        forecast_points=[
            {"ts": "2025-09-25T11:00:00Z", "expected_bookings": 30.5, "std": 1.0},
            {"ts": "2025-09-25T12:00:00Z", "expected_bookings": 45.1, "std": 1.2}
        ],
        model_metadata={"model": "prophet-v2", "version": "2025-09-24"}
    )
    event_bus.publish(high_demand_forecast)

    print("\n--- Simulating a low-demand scenario ---")
    low_demand_forecast = DemandForecastEvent(
        trip_id="trip_2025_10_01_1000",
        forecast_time=datetime.datetime.now().isoformat(),
        horizon_hours=72,
        forecast_points=[
            {"ts": "2025-09-26T11:00:00Z", "expected_bookings": 10.2, "std": 1.0},
            {"ts": "2025-09-26T12:00:00Z", "expected_bookings": 5.7, "std": 1.2}
        ],
        model_metadata={"model": "prophet-v2", "version": "2025-09-24"}
    )
    event_bus.publish(low_demand_forecast)

    print("\n--- Simulation Complete ---")


if __name__ == "__main__":
    main()