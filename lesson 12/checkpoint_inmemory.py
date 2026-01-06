import operator
from typing import Annotated, Literal, TypedDict
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command
from langgraph.checkpoint.memory import InMemorySaver

# When the file execution ends the memory does not persist that is why you
# may want to use a postgresql or sqlite memory storage...
# This works better in Jupyter file
memory = InMemorySaver()
config = {"configurable": {"thread_id": "1"}}


class State(TypedDict):
    nlist: Annotated[list[str], operator.add]


# This return allow to draw the graph correclly if i removet the drawing is not good
def node_a(state: State) -> Command[Literal["b", "c", END]]:
    select = state["nlist"][-1]
    if select == "b":
        next_node = "b"
    elif select == "c":
        next_node = "c"
    elif select == "q":
        next_node = END
    else:
        next_node = END
    # With this you dont need edge conditions
    return Command(update=State(nlist=[select]), goto=[next_node])


def node_b(state: State) -> State:
    return State(nlist=["B"])


def node_c(state: State) -> State:
    return State(nlist=["C"])


builder = StateGraph(State)

# Add nodes
builder.add_node("a", node_a)
builder.add_node("b", node_b)
builder.add_node("c", node_c)

# Add edges
builder.add_edge(START, "a")
builder.add_edge("b", END)
builder.add_edge("c", END)
# No need of this one because im using the Command
# builder.add_conditional_edges("a", conditional_edge)

# Compile with a checkpoint
graph = builder.compile(checkpointer=memory)

while True:
    user = input("b, c, or q to quit: ")
    input_state = State(nlist=[user])
    result = graph.invoke(input_state, config)
    print(result)
    if result["nlist"][-1] == "q":
        print("quit")
        break
