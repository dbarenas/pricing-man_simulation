import datetime
from src.event_bus.memory_bus import MemoryEventBus
from src.agents.pricing_agent import PricingAgent
from src.agents.historical_analysis_agent import HistoricalAnalysisAgent
from src.agents.media_agent import MediaAgent
from src.models.events import DemandForecastEvent, HistoricalDataEvent, MediaImpactScoreEvent

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
    media_agent = MediaAgent("media_agent_v1", event_bus)

    # 3. Agents subscribe to events
    pricing_agent.run()
    historical_agent.run()
    media_agent.run()

    # 4. Add handlers to listen for final outputs
    def price_suggestion_handler(event):
        print(f"[Simulation] Received price suggestion: ${event.suggested_price} for trip {event.trip_id}")

    def promotion_suggestion_handler(event):
        print(f"[Simulation] Received promotion suggestion for trip {event.trip_id}: {event.discount_pct}% discount. Reason: {event.reasoning}")

    def media_impact_handler(event):
        print(f"[Simulation] Received media impact score for trip {event.trip_id}: {event.media_impact_score:.4f} ('{event.campaign_idea}')")

    event_bus.subscribe("price_suggestion.v1", price_suggestion_handler)
    event_bus.subscribe("promotion_suggestion.v1", promotion_suggestion_handler)
    event_bus.subscribe("media_impact_score.v1", media_impact_handler)

    # 5. --- Simulate Demand Forecast Scenarios (No Media Impact) ---
    print("\n--- Simulating Demand Forecasts (No Media Impact) ---")
    high_demand_forecast = DemandForecastEvent(
        trip_id="trip_DF_high",
        forecast_time=datetime.datetime.now().isoformat(),
        horizon_hours=72,
        forecast_points=[{"expected_bookings": 75}],
        model_metadata={"model": "prophet-v2"}
    )
    event_bus.publish(high_demand_forecast)

    low_demand_forecast = DemandForecastEvent(
        trip_id="trip_DF_low",
        forecast_time=datetime.datetime.now().isoformat(),
        horizon_hours=72,
        forecast_points=[{"expected_bookings": 25}],
        model_metadata={"model": "prophet-v2"}
    )
    event_bus.publish(low_demand_forecast)

    # 6. --- Simulate Historical Analysis Scenarios ---
    print("\n--- Simulating Historical Analysis ---")
    poor_historical_data = HistoricalDataEvent(
        trip_id="trip_HA_poor",
        capacity=200,
        historical_bookings=[{'days_before': 7, 'bookings': 70}]
    )
    event_bus.publish(poor_historical_data)

    strong_historical_data = HistoricalDataEvent(
        trip_id="trip_HA_strong",
        capacity=200,
        historical_bookings=[{'days_before': 7, 'bookings': 120}]
    )
    event_bus.publish(strong_historical_data)

    # 7. --- Simulate Media Impact Scenario ---
    print("\n--- Simulating Media Impact on Pricing ---")
    trip_with_media = "trip_MA_impact"

    # First, the media agent launches a campaign. This publishes a MediaImpactScoreEvent.
    media_agent.launch_campaign_for_trip(trip_with_media)

    # Then, a demand forecast for the same trip is published.
    # The PricingAgent will use both events to calculate the final price.
    demand_for_media_trip = DemandForecastEvent(
        trip_id=trip_with_media,
        forecast_time=datetime.datetime.now().isoformat(),
        horizon_hours=48,
        forecast_points=[{"expected_bookings": 60}],
        model_metadata={"model": "prophet-v2"}
    )
    event_bus.publish(demand_for_media_trip)


    print("\n--- Simulation Complete ---")


if __name__ == "__main__":
    main()