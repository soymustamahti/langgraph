from typing import Annotated, List, TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from dotenv import load_dotenv
import os

load_dotenv()


# State definition - just keeping track of conversation messages
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]


# Simple tools for the example - in real life these would hit actual APIs
@tool
def search_knowledge_base(query: str):
    """Search internal docs for technical solutions."""
    # simulated search - normally would query a real knowledge base
    if "wifi" in query.lower():
        return "Solution: Restart the router and check the VLAN settings."
    return "No specific solution found in the docs."


@tool
def create_support_ticket(issue_description: str):
    """Creates a ticket in Jira/ServiceNow for a human technician."""
    # would normally make an API call to your ticketing system
    return f"Ticket #9982 created for: {issue_description}"


tools = [search_knowledge_base, create_support_ticket]

# bind_tools() tells the model what tools are available
model = ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY")).bind_tools(
    tools
)


# this is where the "thinking" happens - model decides what to do next
def agent_node(state: AgentState):
    response = model.invoke(state["messages"])
    return {"messages": [response]}


# ReAct = Reason + Act pattern (think, then use tool, repeat as needed)
builder = StateGraph(AgentState)

builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(tools))

# always start with the agent
builder.add_edge(START, "agent")

# tools_condition checks if agent wants to use a tool or is done
builder.add_conditional_edges(
    "agent",
    tools_condition,
    {"tools": "tools", END: END},  # either go to tools or finish
)

# after running tools, go back to agent to process results
builder.add_edge("tools", "agent")

agent = builder.compile()


initial_message = HumanMessage(content="My wifi dont work, how can i fix it?")
final_result = agent.invoke({"messages": [initial_message]})

print("\n=== Conversation ===")
for msg in final_result["messages"]:
    print(f"\n{msg.__class__.__name__}:")
    print(getattr(msg, "content", msg))
