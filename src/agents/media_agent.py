import random
from src.sdk.agent import Agent
from src.models.events import MediaImpactScoreEvent

class MediaAgent(Agent):
    """
    The MediaAgent simulates creating media campaigns and estimates their impact
    on public interest, publishing the result as an impact score.
    """

    CAMPAIGN_IDEAS = [
        ("Sunset Cruise Special", "Highlight the beautiful sunset views on our evening trips. Target couples and photographers.", 0.15),
        ("Family Fun Day", "Promote a weekend package for families with onboard entertainment for kids.", 0.20),
        ("City Escape Discount", "Offer a discount for weekday commuters looking for a scenic route.", 0.10),
        ("Bad Weather, Good Deal", "A last-minute campaign for rainy days, offering a steep discount to fill seats.", -0.05)
    ]

    def __init__(self, agent_id, event_bus):
        super().__init__(agent_id, event_bus)

    def run(self):
        """
        For this simulation, the run method doesn't subscribe to anything.
        Instead, its main logic is triggered by `launch_campaign_for_trip`.
        """
        print(f"[{self.agent_id}] MediaAgent is online.")
        pass

    def launch_campaign_for_trip(self, trip_id: str):
        """
        Simulates the launch of a new media campaign for a specific trip.
        """
        print(f"[{self.agent_id}] Launching a new media campaign for trip {trip_id}...")

        # In a real system, this could involve LLM calls or complex logic.
        # Here, we'll just pick a random campaign idea.
        campaign_idea, reasoning, base_impact = random.choice(self.CAMPAIGN_IDEAS)

        # Add a bit of randomness to the score
        final_impact_score = round(base_impact + random.uniform(-0.05, 0.05), 4)

        print(f"[{self.agent_id}] Generated campaign idea: '{campaign_idea}' with an estimated impact score of {final_impact_score}")

        media_event = MediaImpactScoreEvent(
            trip_id=trip_id,
            media_impact_score=final_impact_score,
            campaign_idea=campaign_idea,
            reasoning=f"Simulated campaign based on idea: '{reasoning}'. Base impact {base_impact}, final score after random variance."
        )

        self.publish(media_event)
        print(f"[{self.agent_id}] Published media impact score for trip {trip_id}.")