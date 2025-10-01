# Ferry Seat Occupancy Multi-Agent System

This repository contains the starter code for a proactive, asynchronous multi-agent system designed to maximize ferry seat occupancy. It provides a modular and extensible framework for building intelligent agents that can react to various signals (e.g., demand, weather, media) to make optimal pricing and marketing decisions.

## Table of Contents
- [Architecture Overview](#architecture-overview)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Simulation](#running-the-simulation)
  - [Running Tests](#running-tests)
- [How to Extend the System](#how-to-extend-the-system)
  - [Creating a New Agent](#creating-a-new-agent)
  - [Defining a New Event](#defining-a-new-event)
  - [Integrating the New Agent](#integrating-the-new-agent)
- [Connecting to a Large Language Model (LLM)](#connecting-to-a-large-language-model-llm)

---

## Architecture Overview

The system is built around an **asynchronous, event-driven architecture**. This design promotes loose coupling between components and allows for scalability and resilience.

The core components are:
1.  **Event Bus**: The central nervous system of the application. All communication between agents happens via the event bus. This implementation uses an in-memory bus for simplicity, but it can be easily swapped with a production-grade message broker like Kafka or RabbitMQ.
2.  **Agents**: Independent, specialized services that perform specific tasks. Each agent subscribes to events it's interested in, processes them, and may publish new events as a result. Examples include:
    *   The `PricingAgent` listens for `DemandForecastEvent` and `MediaImpactScoreEvent` to publish a `PriceSuggestionEvent`.
    *   The `HistoricalAnalysisAgent` listens for `HistoricalDataEvent` and publishes a `PromotionSuggestionEvent`.
    *   The `MediaAgent` simulates media campaigns and publishes a `MediaImpactScoreEvent`.
3.  **Events**: Plain data objects that represent a fact or a signal within the system (e.g., a new booking, a weather update, a demand forecast). Events are defined using Python `dataclasses` for clear, structured contracts.
4.  **Agent SDK**: A simple Software Development Kit (`src/sdk`) that provides a base `Agent` class. This class handles the boilerplate of subscribing and publishing to the event bus, allowing developers to focus on the agent's logic.

The typical flow is as follows:
- An external or internal event occurs (e.g., a `DemandForecastEvent` is generated).
- The event is published to the event bus.
- One or more agents subscribed to that event type receive it.
- The agents process the event and may perform actions, such as publishing new events.

---

## Project Structure

```
.
├── main.py             # Main script to run the simulation
├── requirements.txt    # Python dependencies
├── src
│   ├── agents
│   │   ├── pricing_agent.py
│   │   ├── historical_analysis_agent.py
│   │   └── media_agent.py   # Simulates media campaigns
│   ├── event_bus
│   │   └── memory_bus.py    # In-memory event bus for local dev
│   ├── models
│   │   └── events.py        # Event data models (dataclasses)
│   └── sdk
│       └── agent.py         # The base Agent SDK class
└── tests
    ├── test_pricing_agent.py
    ├── test_historical_analysis_agent.py
    └── test_media_agent.py
```

---

## Getting Started

### Prerequisites
- Python 3.9+

### Installation
No external dependencies are required for the base implementation. If you add packages, list them in `requirements.txt` and install them:
```bash
pip install -r requirements.txt
```

### Running the Simulation
The `main.py` script initializes the event bus, starts the agents, and simulates a couple of scenarios (high-demand and low-demand).

To run the simulation, execute:
```bash
python main.py
```

You will see output showing the agents subscribing to events, receiving forecasts, and publishing price suggestions.

### Running Tests
The project uses Python's built-in `unittest` framework. To run all tests, use the `discover` command from the root directory:
```bash
python -m unittest discover tests
```

---

## How to Extend the System

The power of this architecture lies in its extensibility. You can easily add new agents to introduce new behaviors.

### 1. Creating a New Agent
Let's create a hypothetical `WeatherAgent` that fetches weather data and publishes a `WeatherUpdateEvent`.

Create a new file `src/agents/weather_agent.py`:
```python
# src/agents/weather_agent.py
from src.sdk.agent import Agent
from src.models.events import WeatherUpdateEvent # We'll define this next

class WeatherAgent(Agent):
    def run(self):
        # In a real agent, this might be on a timer or triggered by another event
        print(f"[{self.agent_id}] Fetching weather forecast...")

        # Dummy weather data
        weather_data = {
            "condition": "sunny",
            "temperature_c": 25,
            "wind_kph": 10
        }

        weather_event = WeatherUpdateEvent(
            trip_id="trip_2025_09_30_1800",
            forecast=weather_data
        )

        self.publish(weather_event)
        print(f"[{self.agent_id}] Published weather update.")

```

### 2. Defining a New Event
Now, define the `WeatherUpdateEvent` in `src/models/events.py`:
```python
# src/models/events.py
from dataclasses import dataclass, field
from typing import Dict, Any

# ... other event classes ...

@dataclass
class WeatherUpdateEvent(BaseEvent):
    trip_id: str
    forecast: Dict[str, Any]
    type: str = "weather_update.v1"
```

### 3. Integrating the New Agent
Finally, add the new agent to the simulation in `main.py`:

```python
# main.py
# ... imports ...
from src.agents.weather_agent import WeatherAgent # Import the new agent

def main():
    # ...
    # 2. Initialize agents
    pricing_agent = PricingAgent("pricing_agent_v1", event_bus)
    weather_agent = WeatherAgent("weather_agent_v1", event_bus) # Add new agent

    # 3. Agents subscribe to events / run
    pricing_agent.run()
    weather_agent.run()
    # ...
```

You would also modify the `PricingAgent` to subscribe to `weather_update.v1` and adjust its pricing logic based on the weather.

---

## Connecting to a Large Language Model (LLM)

You can enhance an agent's decision-making capabilities by connecting it to an LLM like GPT-4. The LLM can be used for complex reasoning, interpreting unstructured data, or generating human-readable justifications for actions.

**Example: An LLM-powered `ProactiveAgent`**

Imagine a `ProactiveAgent` that decides whether to approve a price suggestion. Instead of using hard-coded rules, it could ask an LLM.

**Conceptual Implementation:**

1.  **The Agent's Role**: The agent gathers structured data from various events (`PriceSuggestionEvent`, `WeatherUpdateEvent`, `MediaImpactEvent`).
2.  **Prompt Engineering**: The agent formats this data into a clear, concise prompt for the LLM.
    ```
    System: You are a revenue manager for a ferry company. Your goal is to maximize occupancy and revenue.

    User: Given the following data for trip T-123:
    - Current Occupancy: 35%
    - Demand Score: 0.75 (High)
    - Weather Forecast: Sunny, 22°C
    - Media Sentiment: Positive
    - Suggested Price: $45 (a 15% increase)

    Should I approve this price increase? Provide a 'decision' (APPROVE/REJECT) and a brief 'justification'.
    ```
3.  **API Call**: The agent makes an API call to the LLM service (e.g., OpenAI's API).
4.  **Parse Response**: The agent parses the LLM's response (e.g., a JSON object with `decision` and `justification` keys).
5.  **Take Action**: Based on the parsed response, the agent publishes a new event, like `ActionCommand` (e.g., to approve the price change) or escalates to a human operator.

**Agent Code Snippet (Conceptual):**

```python
# In a hypothetical ProactiveAgent
import openai # Or other LLM library

class ProactiveAgent(Agent):
    # ...
    def handle_price_suggestion(self, event: PriceSuggestionEvent):
        # 1. Gather context from other events/state
        context = self.build_context_for_llm(event)

        # 2. Create the prompt
        prompt = self.create_llm_prompt(context)

        # 3. Call the LLM
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )

        # 4. Parse the decision
        llm_decision = self.parse_llm_response(response)

        # 5. Act on the decision
        if llm_decision['decision'] == 'APPROVE':
            self.publish_approval_command(event, llm_decision['justification'])
```

This approach allows you to embed sophisticated, nuanced reasoning directly into your automated system, moving beyond simple rule-based logic.