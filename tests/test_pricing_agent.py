import unittest
import datetime
from src.event_bus.memory_bus import MemoryEventBus
from src.agents.pricing_agent import PricingAgent
from src.models.events import DemandForecastEvent, PriceSuggestionEvent, MediaImpactScoreEvent

class TestPricingAgent(unittest.TestCase):

    def setUp(self):
        self.event_bus = MemoryEventBus()
        self.pricing_agent = PricingAgent("test_pricing_agent", self.event_bus)
        self.pricing_agent.run()
        self.received_events = []
        self.event_bus.subscribe("price_suggestion.v1", self.price_suggestion_handler)

    def tearDown(self):
        self.received_events = []

    def price_suggestion_handler(self, event: PriceSuggestionEvent):
        self.received_events.append(event)

    def test_high_demand_scenario_no_media(self):
        """Test high-demand forecast with no media impact."""
        high_demand_forecast = DemandForecastEvent(
            trip_id="trip_high_demand",
            forecast_time=datetime.datetime.now().isoformat(),
            horizon_hours=72,
            forecast_points=[{"expected_bookings": 75}],
            model_metadata={"model": "test-model"}
        )
        self.event_bus.publish(high_demand_forecast)

        self.assertEqual(len(self.received_events), 1)
        price_suggestion = self.received_events[0]
        self.assertEqual(price_suggestion.trip_id, "trip_high_demand")
        self.assertEqual(price_suggestion.suggested_price, 35.0) # Base price for high demand
        self.assertEqual(price_suggestion.reasoning["media_adj"], 0.0)

    def test_low_demand_scenario_no_media(self):
        """Test low-demand forecast with no media impact."""
        low_demand_forecast = DemandForecastEvent(
            trip_id="trip_low_demand",
            forecast_time=datetime.datetime.now().isoformat(),
            horizon_hours=72,
            forecast_points=[{"expected_bookings": 25}],
            model_metadata={"model": "test-model"}
        )
        self.event_bus.publish(low_demand_forecast)

        self.assertEqual(len(self.received_events), 1)
        price_suggestion = self.received_events[0]
        self.assertEqual(price_suggestion.trip_id, "trip_low_demand")
        self.assertEqual(price_suggestion.suggested_price, 25.0) # Base price for low demand
        self.assertEqual(price_suggestion.reasoning["media_adj"], 0.0)

    def test_pricing_with_positive_media_impact(self):
        """Test that a positive media score increases the suggested price."""
        trip_id = "trip_positive_media"
        media_impact_score = 0.20  # 20% positive impact

        # 1. Publish media event first
        media_event = MediaImpactScoreEvent(
            trip_id=trip_id,
            media_impact_score=media_impact_score,
            campaign_idea="Test Campaign",
            reasoning="A great test campaign"
        )
        self.event_bus.publish(media_event)

        # 2. Publish demand forecast for the same trip
        demand_forecast = DemandForecastEvent(
            trip_id=trip_id,
            forecast_time=datetime.datetime.now().isoformat(),
            horizon_hours=72,
            forecast_points=[{"expected_bookings": 75}], # High demand
            model_metadata={"model": "test-model"}
        )
        self.event_bus.publish(demand_forecast)

        self.assertEqual(len(self.received_events), 1)
        price_suggestion = self.received_events[0]
        self.assertEqual(price_suggestion.trip_id, trip_id)
        # Expected price = 35.0 * (1 + 0.20) = 42.0
        self.assertAlmostEqual(price_suggestion.suggested_price, 42.0)
        self.assertEqual(price_suggestion.reasoning["media_adj"], media_impact_score)

    def test_pricing_with_negative_media_impact(self):
        """Test that a negative media score decreases the suggested price."""
        trip_id = "trip_negative_media"
        media_impact_score = -0.10  # 10% negative impact

        # 1. Publish media event
        media_event = MediaImpactScoreEvent(
            trip_id=trip_id,
            media_impact_score=media_impact_score,
            campaign_idea="Bad Test Campaign",
            reasoning="A bad test campaign"
        )
        self.event_bus.publish(media_event)

        # 2. Publish demand forecast
        demand_forecast = DemandForecastEvent(
            trip_id=trip_id,
            forecast_time=datetime.datetime.now().isoformat(),
            horizon_hours=72,
            forecast_points=[{"expected_bookings": 30}], # Low demand
            model_metadata={"model": "test-model"}
        )
        self.event_bus.publish(demand_forecast)

        self.assertEqual(len(self.received_events), 1)
        price_suggestion = self.received_events[0]
        self.assertEqual(price_suggestion.trip_id, trip_id)
        # Expected price = 25.0 * (1 - 0.10) = 22.50
        self.assertAlmostEqual(price_suggestion.suggested_price, 22.50)
        self.assertEqual(price_suggestion.reasoning["media_adj"], media_impact_score)

if __name__ == '__main__':
    unittest.main()