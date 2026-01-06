from typing import TypedDict
import random

from langgraph.graph import StateGraph, START, END
from langgraph.types import RetryPolicy


class WeatherState(TypedDict):
    city: str
    temperature: float
    conditions: str


# simulated error
class APIError(Exception):
    pass


def fetch_weather(state: WeatherState):
    city = state["city"]

    # simulate request that fails 70% of the time
    if random.random() < 0.7:
        print(f"❌ API call failed for {city}")
        raise APIError(f"Weather API timeout for {city}")

    print(f"✅ Successfully fetched weather for {city}")

    temp = round(random.uniform(15, 30), 1)
    conditions = random.choice(["Sunny", "Cloudy", "Rainy", "PartiallyCloudy"])

    # Return only the updates to merge into state
    return {"temperature": temp, "conditions": conditions}


def format_result(state: WeatherState):
    print(f"\n🌤️ Weather Report for {state['city']}")
    print(f"Temperature: {state['temperature']}°C")
    print(f"Conditions: {state['conditions']}")
    return state


builder = StateGraph(WeatherState)

builder.add_node(
    "fetch_weather",
    fetch_weather,
    retry_policy=RetryPolicy(
        max_attempts=5,
        initial_interval=1,
        backoff_factor=2.0,
        max_interval=10.0,
        jitter=True,
        retry_on=(APIError,),  # tuple is the safest form
    ),
)

builder.add_node("format_result", format_result)

builder.add_edge(START, "fetch_weather")
builder.add_edge("fetch_weather", "format_result")
builder.add_edge("format_result", END)

graph = builder.compile()

try:
    result = graph.invoke(
        {"city": "San Francisco", "temperature": 0.0, "conditions": ""}
    )
    print(f"\n✅ Final result: {result}")
except Exception as e:
    print(f"\n❌ All retry attempts exhausted: {e}")
