import unittest
import datetime
from src.event_bus.memory_bus import MemoryEventBus
from src.agents.pricing_agent import PricingAgent
from src.models.events import DemandForecastEvent, PriceSuggestionEvent

class TestPricingAgent(unittest.TestCase):

    def setUp(self):
        self.event_bus = MemoryEventBus()
        self.pricing_agent = PricingAgent("test_pricing_agent", self.event_bus)
        self.pricing_agent.run()
        self.received_events = []

    def tearDown(self):
        self.received_events = []

    def price_suggestion_handler(self, event: PriceSuggestionEvent):
        self.received_events.append(event)

    def test_high_demand_scenario(self):
        """
        Test that the pricing agent suggests a higher price for a high-demand forecast.
        """
        self.event_bus.subscribe("price_suggestion.v1", self.price_suggestion_handler)

        high_demand_forecast = DemandForecastEvent(
            trip_id="trip_high_demand",
            forecast_time=datetime.datetime.now().isoformat(),
            horizon_hours=72,
            forecast_points=[
                {"ts": "2025-09-25T11:00:00Z", "expected_bookings": 60.0},
                {"ts": "2025-09-25T12:00:00Z", "expected_bookings": 40.0}
            ],
            model_metadata={"model": "test-model"}
        )
        self.event_bus.publish(high_demand_forecast)

        self.assertEqual(len(self.received_events), 1)
        price_suggestion = self.received_events[0]
        self.assertEqual(price_suggestion.trip_id, "trip_high_demand")
        self.assertEqual(price_suggestion.suggested_price, 35.0)
        self.assertEqual(price_suggestion.reasoning["demand_score"], 1.0)


    def test_low_demand_scenario(self):
        """
        Test that the pricing agent suggests a lower price for a low-demand forecast.
        """
        self.event_bus.subscribe("price_suggestion.v1", self.price_suggestion_handler)

        low_demand_forecast = DemandForecastEvent(
            trip_id="trip_low_demand",
            forecast_time=datetime.datetime.now().isoformat(),
            horizon_hours=72,
            forecast_points=[
                {"ts": "2025-09-26T11:00:00Z", "expected_bookings": 15.0},
                {"ts": "2025-09-26T12:00:00Z", "expected_bookings": 10.0}
            ],
            model_metadata={"model": "test-model"}
        )
        self.event_bus.publish(low_demand_forecast)

        self.assertEqual(len(self.received_events), 1)
        price_suggestion = self.received_events[0]
        self.assertEqual(price_suggestion.trip_id, "trip_low_demand")
        self.assertEqual(price_suggestion.suggested_price, 25.0)
        self.assertEqual(price_suggestion.reasoning["demand_score"], 0.25)

if __name__ == '__main__':
    unittest.main()