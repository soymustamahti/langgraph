from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.tools import tool
from langchain.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()


# --- TOOLS ---
@tool
def search_knowledge_base(query: str):
    """Search internal docs for technical solutions."""
    # Simulated search result
    if "wifi" in query.lower():
        return "Solution: Restart the router and check the VLAN settings."
    return "No specific solution found in the docs."


@tool
def create_support_ticket(issue_description: str):
    """Creates a ticket in Jira/ServiceNow for a human technician."""
    return f"Ticket #9982 created for: {issue_description}"


tools = [search_knowledge_base, create_support_ticket]

# --- MODEL ---
# create_agent needs a model. We don't bind_tools here because
# create_agent will do it for us internally!
model = ChatOpenAI(model="gpt-4o")

# --- THE AGENT ---
# This one line creates the entire graph (Nodes: START -> Agent -> Action -> Agent... -> END)
agent = create_agent(
    model,
    tools=tools,
    system_prompt="You are a tech support expert. Search first, then create a ticket if no solution exists.",
)


final_result = agent.invoke(input="My wifi dont work, how can i fix it?")

print(final_result)
