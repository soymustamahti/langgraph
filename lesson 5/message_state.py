from langgraph.graph import StateGraph, START, END, MessagesState
from langchain_core.messages import HumanMessage, AIMessage


class MyGraphState(MessagesState):
    # no need to do:
    # messages: Annotated[List[BaseMessage], add_messages]
    # Because when we inherit from MessagesState we already have it
    turn_count: int


def user_node(state: MyGraphState) -> dict:
    print("---Execute User Node...")
    return {"messages": HumanMessage(content="What is the whether today ?")}


def ai_node(state: MyGraphState) -> dict:
    print("---Execute AI Node...")

    last_message = state["messages"][-1].content

    response_content = (
        f"Im aware of your message '{last_message}'. "
        "But im not a real AI so i can not tell you what the wether is, "
        "but at least the code works !!"
    )

    return {"messages": AIMessage(content=response_content)}


def turn_cound_node(state: MyGraphState):
    return {"turn_count": state["turn_count"] + 1}


graphe = StateGraph(MyGraphState)

graphe.add_node(user_node)
graphe.add_node(ai_node)
graphe.add_node(turn_cound_node)

graphe.add_edge(START, "user_node")
graphe.add_edge("user_node", "ai_node")
graphe.add_edge("ai_node", "turn_cound_node")
graphe.add_edge("turn_cound_node", END)

agent = graphe.compile()

inital_state = {"messages": [], "turn_count": 0}

final_state = agent.invoke(inital_state)

print("-----Final State Graph------")
print(final_state)
print("-" * 30)
