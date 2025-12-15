from langgraph.graph import StateGraph, START, END
from typing import Annotated, List, TypedDict
from langgraph.graph.message import add_messages


# 1- Define State
class SimpleState(TypedDict):
    messages: Annotated[list, add_messages]


graph = StateGraph(SimpleState)


# 2. Define Nodes
def say_hello(state: SimpleState):
    print("Execute Node Hello !")
    return {"messages": ["Hello"]}


def say_world(state: SimpleState):
    print("Execute Node World !")
    return {"messages": ["World"]}


graph.add_node("say_hello", say_hello)
graph.add_node("say_world", say_world)

# 3. Link nodes with edges
graph.add_edge(START, "say_hello")
graph.add_edge("say_hello", "say_world")
graph.add_edge("say_world", END)

# 4. Compline Graphe
agent = graph.compile()

# 5. Preview the graph (you need to install "grandalf" lib for this)
print(agent.get_graph().draw_ascii())

# 6. Run Graphg
initial_starte = {"message": []}

final_state = agent.invoke(initial_starte)

print("Final start")
print(final_state)
