from typing import Annotated, List, TypedDict
from langgraph.graph import StateGraph, START, END

from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI

import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]


def chat_node(state: AgentState) -> dict:

    conversation_history = state["messages"]

    response = llm.invoke(conversation_history)

    return {"messages": response}


graph = StateGraph(AgentState)

graph.add_node("chat_node", chat_node)

graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

agent = graph.compile()


# Lets start sending messages
# Turn 1
message_one = HumanMessage(content="Hello, how are you ? Im Musta")

turn_one_state = agent.invoke({"messages": message_one})

print("-----Graph state after first run------")
print(turn_one_state)
print("-" * 30)


# Turn 2
message_two = HumanMessage(content="I would like to know what is you favorite color.")

# We we start using diferent nodes the "add_message" will take care of binding the the previous state to the current state...
# Here we running it like a new request to the model manual...
turn_two_state = agent.invoke({"messages": turn_one_state["messages"] + [message_two]})

print("-----Graph state after first run------")
print(turn_two_state)
print("-" * 30)
