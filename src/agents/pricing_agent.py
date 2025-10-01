import datetime
from src.sdk.agent import Agent
from src.models.events import DemandForecastEvent, PriceSuggestionEvent, MediaImpactScoreEvent

class PricingAgent(Agent):
    """
    The PricingAgent subscribes to demand forecasts and media impact scores
    to propose prices.
    """
    def __init__(self, agent_id, event_bus):
        super().__init__(agent_id, event_bus)
        self.media_impact_scores = {}  # In-memory store for trip_id -> score

    def run(self):
        """
        Subscribes to demand forecast and media impact events.
        """
        self.subscribe("demand_forecast.v1", self.handle_demand_forecast)
        self.subscribe("media_impact_score.v1", self.handle_media_impact)
        print(f"[{self.agent_id}] Subscribed to 'demand_forecast.v1' and 'media_impact_score.v1'")

    def handle_media_impact(self, event: MediaImpactScoreEvent):
        """
        Handles a media impact score event by storing the latest score for the trip.
        """
        print(f"[{self.agent_id}] Received media impact score of {event.media_impact_score:.4f} for trip {event.trip_id}")
        self.media_impact_scores[event.trip_id] = event.media_impact_score

    def handle_demand_forecast(self, event: DemandForecastEvent):
        """
        Handles a demand forecast event and publishes a price suggestion,
        adjusting for any known media impact.
        """
        print(f"[{self.agent_id}] Received demand forecast for trip {event.trip_id}")

        # Basic pricing logic: higher demand -> higher price
        total_expected_bookings = sum(p["expected_bookings"] for p in event.forecast_points)
        demand_score = total_expected_bookings / 100  # Normalize score

        if demand_score > 0.5:
            base_price = 35.0
            confidence = 0.8
        else:
            base_price = 25.0
            confidence = 0.7

        # Adjust price based on media impact, if available
        media_adj = self.media_impact_scores.get(event.trip_id, 0.0)

        # The adjustment is a multiplier. E.g., a score of 0.15 results in a 15% price increase.
        final_price = round(base_price * (1 + media_adj), 2)

        reasoning = {
            "demand_score": round(demand_score, 4),
            "weather_adj": 0.0,  # Placeholder for future weather agent
            "media_adj": media_adj
        }

        print(f"[{self.agent_id}] Trip {event.trip_id}: Base price ${base_price}, Media Adj {media_adj:.2%}, Final Price ${final_price}")

        price_suggestion = PriceSuggestionEvent(
            trip_id=event.trip_id,
            seat_class="standard",
            suggested_price=final_price,
            reasoning=reasoning,
            valid_until=(datetime.datetime.now() + datetime.timedelta(hours=1)).isoformat(),
            confidence=confidence,
        )

        self.publish(price_suggestion)
        print(f"[{self.agent_id}] Published price suggestion for trip {event.trip_id}: ${final_price}")