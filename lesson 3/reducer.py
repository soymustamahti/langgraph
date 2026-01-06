from langgraph.graph import StateGraph, START, END
from typing import Annotated, List, TypedDict
from operator import add


# 1. Without Reducer
# since im not using Annotated it uses the default reducer...
class StateWithoutReducer(TypedDict):
    count: int
    animals: List[str]


def node_to_update(state: StateWithoutReducer) -> dict:
    return {"count": 1, "animals": ["dog"]}


initial_state = {"count": 5, "animals": ["lion", "buffalo"]}


# 2. With Reducer
def custom_count_reducer(current: int, new: int) -> int:
    return current + new


# The custom reducer can be complex or just simple, here im doing something complex...
def custom_animal_reducer(current: list[str], new: list[str]) -> list[str]:
    for animal in new:
        current.append(animal)
    return current


class StateWithReducer(TypedDict):
    count: Annotated[int, custom_count_reducer]
    animals: Annotated[List[str], custom_animal_reducer]


# 3. With Reducer and "operator" lib for animals append
class StateWithReducerAndOperatorLib(TypedDict):
    # We reuse the custom_count_reducer for count
    count: Annotated[int, custom_count_reducer]
    # We use add from "operator"
    animals: Annotated[List[str], add]


# TODO: check what is "callable"
def run_example(
    name: str, state_schema: type, node_func: callable, initial_state: dict
):

    print(f"Running Example {name}")
    graph = StateGraph(state_schema)

    # Add nodes
    graph.add_node("update_node", node_func)

    # Add edges
    graph.add_edge(START, "update_node")
    graph.add_edge("update_node", END)

    app = graph.compile()

    final_state = app.invoke(initial_state)

    print(f"Initial State: {initial_state}")
    print(f"Final State: {final_state}")


# Run without Reducer
print("\nRun without Reducer")

run_example(
    name="Without Reducer",
    state_schema=StateWithoutReducer,
    node_func=node_to_update,
    initial_state=initial_state,
)
# output ->
# Initial State: {'count': 5, 'animals': ['lion', 'buffalo']}
# Final State: {'count': 1, 'animals': ['dog']}
# This is because since im not using a reducer it used the default one
# And the default one it overwrites the state variables...

# Run with Reducer
print("\nRun with Reducer")

run_example(
    name="With Reducer",
    state_schema=StateWithReducer,
    node_func=node_to_update,
    initial_state=initial_state,
)
# output ->
# Initial State: {'count': 5, 'animals': ['lion', 'buffalo']}
# Final State: {'count': 6, 'animals': ['lion', 'buffalo', 'dog']}
# This is because is using the custom reducer that append the animals list and increments the count


# Instead of using the custom_animal_reducer we can import and use libs that use pure functions to do so
# We can use the lib "operator" with the add function to do it...
print("\nRun with Reducer and operator lib")

run_example(
    name="With Reducer",
    state_schema=StateWithReducerAndOperatorLib,
    node_func=node_to_update,
    initial_state=initial_state,
)
# Since add function looks like:
# def add(a, b):
# "Same as a + b."
# return a + b
# We can use it as reducer, because is a pure function...
