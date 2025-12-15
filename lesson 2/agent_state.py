from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated, List

# add_message is a reducer for llm to have the conversation historic -> return HumanMessage class
from langgraph.graph.message import add_messages

from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage


# Schema
""" This is the schema that we will have
    - messages
    - step_count
    - private_data
    
"""


# Node
def node_a(state):
    print("Executing Node A...")
    return {"messages": ["Step A Completed"], "step_count": 1}


def node_b(state):
    print("Executing Node B...")
    if isinstance(state, dict):
        step_count = state["step_count"]
    else:
        step_count = state.step_count

    print(f"Current step count from state: {step_count}")

    return {"messages": ["Step B Completed"], "step_count": 1}


def build_and_run_graph(state_schema, initial_state):
    print("Start building and running graph")

    graph = StateGraph(state_schema)

    graph.add_node("node_a", node_a)
    graph.add_node("node_b", node_b)

    graph.add_edge(START, "node_a")
    graph.add_edge("node_a", "node_b")
    graph.add_edge("node_b", END)

    agent = graph.compile()

    final_state = agent.invoke(initial_state)

    print("Final state")
    print(final_state)


# Using a Plan Dictionary


def create_dict_state():
    return {"messages": [], "step_count": 0, "private_data": None}


print("\nDic schema")
build_and_run_graph(dict, create_dict_state)
# output -> {'messages': ['Step B Completed'], 'step_count': 1}

# Why i that i dont see 'Step A Completed' and 'Step B Completed' ?
# That is because the default reducer is going to overwrite a state value
# and thats why we dont see 'Step A Completed' and 'Step B Completed'
# And that why also the 'step_count' dont increment... for that we need a costum reducer


# Using TypeDict


# lets create a custom reducer to increment "step_count"
def add_custom_reducer(current: int, new: int) -> int:
    return current + new


class TypeDictState(TypedDict):
    messages: Annotated[List[str], add_messages]
    step_count: Annotated[int, add_custom_reducer]
    private_data: str


print("\nTypeDic schema")
build_and_run_graph(
    TypeDictState, {"messages": [], "step_count": 0, "private_data": ""}
)
# output ->
"""
{'messages': [HumanMessage(content='Step A Completed',{more_data}),
HumanMessage(content='Step B Completed', {more_data})],'step_count': 2, 'private_data': ''}
    """
# Here you can see all the steps because we are using add_messages reducer which use HumanMessage class
# because is for llms
# ana we can see that our add_custom_reducer custom reducer worked


# Using Pydantic
class PydanticState(BaseModel):
    # We use default_factory to make sure that each instance of PydanticState has a new list
    # otherwise pydantic is going to share the list between the instances you create...
    # we want each instance come with fresh list
    messages: Annotated[List[BaseMessage], add_messages] = Field(default_factory=list)
    step_count: Annotated[int, add_custom_reducer] = Field(default=0)
    private_data: str = Field(default="")


print("\nPydantic schema")
build_and_run_graph(PydanticState, PydanticState())


# Important to know TypeDic has better performance that Pydantic, but Pydantic allow you to make validation
# and give you more options...
