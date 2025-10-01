from src.sdk.agent import Agent
from src.models.events import HistoricalDataEvent, PromotionSuggestionEvent

class HistoricalAnalysisAgent(Agent):
    """
    The HistoricalAnalysisAgent analyzes historical booking data to identify
    opportunities for promotions.
    """
    PROMOTION_THRESHOLD = 0.4  # Suggest promotion if fill rate is below 40%
    PROMOTION_DISCOUNT_PCT = 15 # Suggest a 15% discount

    def __init__(self, agent_id, event_bus):
        super().__init__(agent_id, event_bus)

    def run(self):
        """
        Subscribes to historical data events.
        """
        self.subscribe("historical_data.v1", self.handle_historical_data)
        print(f"[{self.agent_id}] Subscribed to 'historical_data.v1'")

    def handle_historical_data(self, event: HistoricalDataEvent):
        """
        Handles a historical data event and decides whether to suggest a promotion.
        """
        print(f"[{self.agent_id}] Received historical data for trip {event.trip_id}")

        if not event.historical_bookings:
            print(f"[{self.agent_id}] No historical booking data to analyze for trip {event.trip_id}")
            return

        # Simple heuristic: check the booking numbers from the most recent historical data point
        # (i.e., the one with the minimum 'days_before' value).
        latest_data_point = min(event.historical_bookings, key=lambda x: x['days_before'])

        latest_bookings = latest_data_point['bookings']
        fill_rate = latest_bookings / event.capacity

        print(f"[{self.agent_id}] Latest historical fill rate for trip {event.trip_id} was {fill_rate:.2%} ({latest_bookings}/{event.capacity} bookings at T-{latest_data_point['days_before']} days).")

        if fill_rate < self.PROMOTION_THRESHOLD:
            reasoning = (
                f"Historical fill rate of {fill_rate:.2%} is below the "
                f"{self.PROMOTION_THRESHOLD:.0%} threshold. A promotion is recommended."
            )

            promotion_suggestion = PromotionSuggestionEvent(
                trip_id=event.trip_id,
                discount_pct=self.PROMOTION_DISCOUNT_PCT,
                reasoning=reasoning
            )

            self.publish(promotion_suggestion)
            print(f"[{self.agent_id}] Published promotion suggestion for trip {event.trip_id}.")
        else:
            print(f"[{self.agent_id}] Historical performance is strong. No promotion needed for trip {event.trip_id}.")