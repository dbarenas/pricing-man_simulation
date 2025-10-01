import unittest
from src.event_bus.memory_bus import MemoryEventBus
from src.agents.historical_analysis_agent import HistoricalAnalysisAgent
from src.models.events import HistoricalDataEvent, PromotionSuggestionEvent

class TestHistoricalAnalysisAgent(unittest.TestCase):

    def setUp(self):
        self.event_bus = MemoryEventBus()
        self.historical_agent = HistoricalAnalysisAgent("test_historical_agent", self.event_bus)
        self.historical_agent.run()
        self.received_events = []
        self.event_bus.subscribe("promotion_suggestion.v1", self.promotion_suggestion_handler)

    def tearDown(self):
        self.received_events = []

    def promotion_suggestion_handler(self, event: PromotionSuggestionEvent):
        self.received_events.append(event)

    def test_promotion_triggered_for_poor_performance(self):
        """
        Test that a promotion is suggested when historical fill rate is below the threshold.
        """
        poor_historical_data = HistoricalDataEvent(
            trip_id="trip_poor",
            capacity=200,
            historical_bookings=[
                {'days_before': 14, 'bookings': 50},
                {'days_before': 7, 'bookings': 70}  # 35% fill rate
            ]
        )
        self.event_bus.publish(poor_historical_data)

        self.assertEqual(len(self.received_events), 1)
        promotion_suggestion = self.received_events[0]
        self.assertEqual(promotion_suggestion.trip_id, "trip_poor")
        self.assertEqual(promotion_suggestion.discount_pct, 15)
        self.assertIn("below the 40% threshold", promotion_suggestion.reasoning)

    def test_no_promotion_for_strong_performance(self):
        """
        Test that no promotion is suggested when historical fill rate is above the threshold.
        """
        strong_historical_data = HistoricalDataEvent(
            trip_id="trip_strong",
            capacity=200,
            historical_bookings=[
                {'days_before': 14, 'bookings': 100},
                {'days_before': 7, 'bookings': 120}  # 60% fill rate
            ]
        )
        self.event_bus.publish(strong_historical_data)

        self.assertEqual(len(self.received_events), 0)

    def test_no_promotion_for_empty_historical_data(self):
        """
        Test that no promotion is suggested when there is no historical data to analyze.
        """
        empty_historical_data = HistoricalDataEvent(
            trip_id="trip_empty",
            capacity=200,
            historical_bookings=[]
        )
        self.event_bus.publish(empty_historical_data)

        self.assertEqual(len(self.received_events), 0)

if __name__ == '__main__':
    unittest.main()