import datetime
from src.event_bus.memory_bus import MemoryEventBus
from src.agents.pricing_agent import PricingAgent
from src.agents.historical_analysis_agent import HistoricalAnalysisAgent
from src.models.events import DemandForecastEvent, HistoricalDataEvent

def main():
    """
    Main function to run the simulation.
    """
    print("--- Ferry Seat Occupancy Simulation ---")

    # 1. Initialize the event bus
    event_bus = MemoryEventBus()

    # 2. Initialize agents
    pricing_agent = PricingAgent("pricing_agent_v1", event_bus)
    historical_agent = HistoricalAnalysisAgent("historical_analysis_agent_v1", event_bus)

    # 3. Agents subscribe to events
    pricing_agent.run()
    historical_agent.run()

    # 4. Add handlers to listen for final outputs
    def price_suggestion_handler(event):
        print(f"[Simulation] Received price suggestion: ${event.suggested_price} for trip {event.trip_id}")

    def promotion_suggestion_handler(event):
        print(f"[Simulation] Received promotion suggestion for trip {event.trip_id}: {event.discount_pct}% discount. Reason: {event.reasoning}")

    event_bus.subscribe("price_suggestion.v1", price_suggestion_handler)
    event_bus.subscribe("promotion_suggestion.v1", promotion_suggestion_handler)

    # 5. --- Simulate Demand Forecast Scenarios ---
    print("\n--- Simulating Demand Forecasts ---")
    high_demand_forecast = DemandForecastEvent(
        trip_id="trip_DF_high",
        forecast_time=datetime.datetime.now().isoformat(),
        horizon_hours=72,
        forecast_points=[
            {"ts": "2025-09-25T11:00:00Z", "expected_bookings": 30.5, "std": 1.0},
            {"ts": "2025-09-25T12:00:00Z", "expected_bookings": 45.1, "std": 1.2}
        ],
        model_metadata={"model": "prophet-v2", "version": "2025-09-24"}
    )
    event_bus.publish(high_demand_forecast)

    low_demand_forecast = DemandForecastEvent(
        trip_id="trip_DF_low",
        forecast_time=datetime.datetime.now().isoformat(),
        horizon_hours=72,
        forecast_points=[
            {"ts": "2025-09-26T11:00:00Z", "expected_bookings": 10.2, "std": 1.0},
            {"ts": "2025-09-26T12:00:00Z", "expected_bookings": 5.7, "std": 1.2}
        ],
        model_metadata={"model": "prophet-v2", "version": "2025-09-24"}
    )
    event_bus.publish(low_demand_forecast)

    # 6. --- Simulate Historical Analysis Scenarios ---
    print("\n--- Simulating Historical Analysis ---")
    # Scenario where historical performance was poor -> should trigger a promotion
    poor_historical_data = HistoricalDataEvent(
        trip_id="trip_HA_poor",
        capacity=200,
        historical_bookings=[
            {'days_before': 14, 'bookings': 50},
            {'days_before': 7, 'bookings': 70} # 70/200 = 35% fill rate < 40% threshold
        ]
    )
    event_bus.publish(poor_historical_data)

    # Scenario where historical performance was strong -> should NOT trigger a promotion
    strong_historical_data = HistoricalDataEvent(
        trip_id="trip_HA_strong",
        capacity=200,
        historical_bookings=[
            {'days_before': 14, 'bookings': 100},
            {'days_before': 7, 'bookings': 120} # 120/200 = 60% fill rate > 40% threshold
        ]
    )
    event_bus.publish(strong_historical_data)


    print("\n--- Simulation Complete ---")


if __name__ == "__main__":
    main()