from typing import TypedDict, List, Annotated
from langgraph.graph import StateGraph, START, END
from operator import add


class GraphState(TypedDict):
    input: str
    execution_path: Annotated[List[str], add]


def node_a(state: GraphState) -> dict:
    print("Executing Node A...")

    return {"execution_path": ["node_a"]}


def node_b(state: GraphState) -> dict:
    print("Executing Node B...")

    return {"execution_path": ["node_b"]}


def node_c(state: GraphState) -> dict:
    print("Executing Node C...")

    return {"execution_path": ["node_c"]}


def node_d(state: GraphState) -> dict:
    print("Executing Node D...")

    return {"execution_path": ["node_d"]}


def should_continue(state: GraphState) -> str:
    if "go_to_c" in state["input"]:
        print("Went to the C node")
        return "node_c"
    else:
        print("Went to the D node")
        return "node_d"


graph = StateGraph(GraphState)

graph.add_node(node_a)
graph.add_node(node_b)
graph.add_node(node_c)
graph.add_node(node_d)

graph.add_edge(START, "node_a")
graph.add_edge("node_a", "node_b")

graph.add_conditional_edges("node_b", should_continue)

graph.add_edge("node_c", END)
graph.add_edge("node_d", END)

agent = graph.compile()

# Depending of the input used you will be redirected to a diferent node
initial_state = {
    "input": "You will have to go to the D node!"
    # "input": "You will have to go to the C node! go_to_c"
}

finale_state = agent.invoke(initial_state)

print("Final State and path execution")
print(finale_state)
