from collections import defaultdict

class MemoryEventBus:
    """
    An in-memory event bus for local development and testing.
    """
    def __init__(self):
        self.subscribers = defaultdict(list)

    def subscribe(self, event_type, handler):
        """
        Subscribes a handler to a specific event type.
        """
        self.subscribers[event_type].append(handler)

    def publish(self, event):
        """
        Publishes an event to all subscribed handlers.
        """
        event_type = event.type
        if event_type in self.subscribers:
            for handler in self.subscribers[event_type]:
                handler(event)