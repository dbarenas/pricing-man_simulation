from dataclasses import dataclass
from typing import List, Dict, Any


# This is a base class for events, not intended to be instantiated directly.
class BaseEvent:
    # All event subclasses should have a 'type' attribute.
    pass


@dataclass
class DemandForecastEvent(BaseEvent):
    trip_id: str
    forecast_time: str
    horizon_hours: int
    forecast_points: List[Dict[str, Any]]
    model_metadata: Dict[str, str]
    type: str = "demand_forecast.v1"


@dataclass
class PriceSuggestionEvent(BaseEvent):
    trip_id: str
    seat_class: str
    suggested_price: float
    reasoning: Dict[str, float]
    valid_until: str
    confidence: float
    type: str = "price_suggestion.v1"