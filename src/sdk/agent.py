from abc import ABC, abstractmethod

class Agent(ABC):
    """
    The base class for all agents.
    """
    def __init__(self, agent_id, event_bus):
        self.agent_id = agent_id
        self.event_bus = event_bus

    def subscribe(self, event_type, handler):
        """
        Subscribes the agent to a specific event type.
        The handler will be called when an event of that type is published.
        """
        self.event_bus.subscribe(event_type, handler)

    def publish(self, event):
        """
        Publishes an event to the event bus.
        """
        self.event_bus.publish(event)

    @abstractmethod
    def run(self):
        """
        The main loop for the agent.
        """
        pass