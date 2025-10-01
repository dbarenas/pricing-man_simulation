import datetime
from src.sdk.agent import Agent
from src.models.events import DemandForecastEvent, PriceSuggestionEvent

class PricingAgent(Agent):
    """
    The PricingAgent subscribes to demand forecasts and proposes prices.
    """
    def __init__(self, agent_id, event_bus):
        super().__init__(agent_id, event_bus)

    def run(self):
        """
        Subscribes to demand forecast events.
        """
        self.subscribe("demand_forecast.v1", self.handle_demand_forecast)
        print(f"[{self.agent_id}] Subscribed to 'demand_forecast.v1'")

    def handle_demand_forecast(self, event: DemandForecastEvent):
        """
        Handles a demand forecast event and publishes a price suggestion.
        """
        print(f"[{self.agent_id}] Received demand forecast for trip {event.trip_id}")

        # Basic pricing logic: higher demand -> higher price
        # This is a placeholder for a more sophisticated model.
        total_expected_bookings = sum(p["expected_bookings"] for p in event.forecast_points)
        demand_score = total_expected_bookings / 100  # Normalize score

        if demand_score > 0.5:
            suggested_price = 35.0
            confidence = 0.8
        else:
            suggested_price = 25.0
            confidence = 0.7

        reasoning = {
            "demand_score": round(demand_score, 4),
            "weather_adj": 0.0,
            "media_adj": 0.0
        }

        price_suggestion = PriceSuggestionEvent(
            trip_id=event.trip_id,
            seat_class="standard",
            suggested_price=suggested_price,
            reasoning=reasoning,
            valid_until=(datetime.datetime.now() + datetime.timedelta(hours=1)).isoformat(),
            confidence=confidence,
        )

        self.publish(price_suggestion)
        print(f"[{self.agent_id}] Published price suggestion for trip {event.trip_id}: ${suggested_price}")