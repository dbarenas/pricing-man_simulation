import unittest
from src.event_bus.memory_bus import MemoryEventBus
from src.agents.media_agent import MediaAgent
from src.models.events import MediaImpactScoreEvent

class TestMediaAgent(unittest.TestCase):

    def setUp(self):
        self.event_bus = MemoryEventBus()
        self.media_agent = MediaAgent("test_media_agent", self.event_bus)
        self.media_agent.run()
        self.received_events = []
        self.event_bus.subscribe("media_impact_score.v1", self.media_impact_handler)

    def tearDown(self):
        self.received_events = []

    def media_impact_handler(self, event: MediaImpactScoreEvent):
        self.received_events.append(event)

    def test_launch_campaign_publishes_event(self):
        """
        Test that launching a campaign publishes a MediaImpactScoreEvent.
        """
        trip_id = "test_trip_123"
        self.media_agent.launch_campaign_for_trip(trip_id)

        self.assertEqual(len(self.received_events), 1)
        event = self.received_events[0]
        self.assertIsInstance(event, MediaImpactScoreEvent)
        self.assertEqual(event.trip_id, trip_id)
        self.assertIsInstance(event.media_impact_score, float)
        self.assertIsInstance(event.campaign_idea, str)
        self.assertTrue(len(event.campaign_idea) > 0)
        self.assertIsInstance(event.reasoning, str)

if __name__ == '__main__':
    unittest.main()