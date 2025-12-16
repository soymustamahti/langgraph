import os
from typing import Annotated, TypedDict, List

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]


@tool
def add_numbers(a: float, b: float) -> float:
    return a + b


@tool
def get_lesson_plan(topic: str) -> str:
    # Return a short learning plan for a given topic.
    topic = topic.strip()
    return (
        f"Mini plan for '{topic}':\n"
        "- Learn the basics\n"
        "- Build a small project\n"
        "- Add tests + edge cases\n"
        "- Measure cost/latency\n"
        "- Ship it as an API\n"
    )


TOOLS = [add_numbers, get_lesson_plan]


def assistant_node(state: AgentState) -> dict:
    print("Executing 'assistant_node'...")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing OPENAI_API_KEY. Add it to `.env` (see `.env.example`) to run this lesson."
        )

    llm = ChatOpenAI(model="gpt-4o", api_key=api_key).bind_tools(TOOLS)
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


builder = StateGraph(AgentState)

builder.add_node("assistant", assistant_node)
builder.add_node("tools", ToolNode(TOOLS))

builder.add_edge(START, "assistant")

# If the model asked for a tool call -> go to tools, otherwise end.
builder.add_conditional_edges(
    "assistant", tools_condition, {"tools": "tools", END: END}
)

# After tool runs, go back to the assistant to let it use the tool output.
builder.add_edge("tools", "assistant")

agent = builder.compile()

print(agent.get_graph().draw_ascii())

initial_state: AgentState = {
    "messages": [
        HumanMessage(
            content=(
                "1) Use the add_numbers tool to compute 19.5 + 2.25.\n"
                "2) Then use get_lesson_plan for topic 'LangGraph tools'.\n"
                "3) Finally summarize both results in 2 bullet points."
            )
        )
    ]
}

final_state = agent.invoke(initial_state)

print("\nFinal Messages")
for message in final_state["messages"]:
    print(f"\n--- {message.__class__.__name__} ---")
    print(getattr(message, "content", message))
