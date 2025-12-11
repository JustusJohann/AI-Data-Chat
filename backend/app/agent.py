from typing import Annotated, Literal, Sequence
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_core.tools import StructuredTool
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

# State definition
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

SYSTEM_PROMPT = """You are an expert Data Analyst. Your goal is to answer the user's questions about the database.

Follow this process strictly:
1. **Investigate**: Always start by querying the `information_schema` to understand the tables and columns. NEVER guess column names.
2. **Query**: Run SQL queries to fetch the data needed to answer the question.
3. **Refine**: If a query fails, analyze the error, fix the SQL, and try again.
4. **Answer**: Provide a clear summary of the data and key insights.

When you have the answer, just respond with the final text.
"""

from langgraph.checkpoint.memory import MemorySaver

def create_agent_graph(tools: list[StructuredTool]):
    """
    Creates and compiles the LangGraph agent with the provided tools.
    """
    
    # Initialize the LLM
    llm = ChatGroq(
        temperature=0,
        #model_name="llama-3.3-70b-versatile",
        model_name="openai/gpt-oss-20b"
    )
    
    # Bind tools to the LLM
    llm_with_tools = llm.bind_tools(tools)
    
    # Define the nodes
    def agent_node(state: AgentState):
        messages = state["messages"]
        # Ensure system prompt is meant to be respected. 
        if not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)
            
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    # Define the tool node
    tool_node = ToolNode(tools)

    # Define logic for conditional edge
    def should_continue(state: AgentState) -> Literal["tools", END]:
        messages = state["messages"]
        last_message = messages[-1]
        
        if last_message.tool_calls:
            return "tools"
        return END

    # Build the graph
    workflow = StateGraph(AgentState)
    
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)
    
    workflow.set_entry_point("agent")
    
    workflow.add_conditional_edges(
        "agent",
        should_continue,
    )
    
    workflow.add_edge("tools", "agent")
    
    # Add checkpointer for memory
    checkpointer = MemorySaver()
    
    return workflow.compile(checkpointer=checkpointer)
