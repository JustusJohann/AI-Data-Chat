import os
import json
from contextlib import asynccontextmanager
from typing import List, Optional, Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from backend.app.mcp_client import mcp_client
from backend.app.agent import create_agent_graph

# Load environment variables
load_dotenv()

# Global state for the agent graph
agent_graph = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events:
    1. Connect to MCP Server.
    2. Initialize Agent Graph with tools.
    """
    global agent_graph
    try:
        print("Starting up: Connecting to MCP server...")
        await mcp_client.connect()
        
        print("Fetching tools...")
        tools = await mcp_client.get_tools()
        
        print(f"Initializing agent with {len(tools)} tools...")
        agent_graph = create_agent_graph(tools)
        
        yield
    except Exception as e:
        print(f"Startup error: {e}")
        raise
    finally:
        print("Shutting down: cleaning up resources...")
        await mcp_client.cleanup()

app = FastAPI(lifespan=lifespan)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None
    schema_context: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    data: Optional[Any] = None
    thread_id: str

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    global agent_graph
    if not agent_graph:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    # Run the graph
    try:
        # Use provided thread_id or generate a new one
        import uuid
        thread_id = request.thread_id or str(uuid.uuid4())
        
        config = {"configurable": {"thread_id": thread_id}}
        
        initial_state = {"messages": [HumanMessage(content=request.message)]}
        result = await agent_graph.ainvoke(initial_state, config=config)
        
        messages = result["messages"]
        final_message = messages[-1]
        
        if not isinstance(final_message, AIMessage):
            raise HTTPException(status_code=500, detail="Unexpected final message type")
            
        answer = final_message.content
        
        # Extract raw data from the last ToolMessage if present
        # Look backwards for the last ToolMessage
        raw_data = None
        for msg in reversed(messages):
            if isinstance(msg, ToolMessage):
                try:
                    # Attempt to parse the content as JSON
                    # The content from MCP might be a stringified JSON or just a string
                    content = msg.content
                    # If it's a string that looks like JSON, parse it
                    if isinstance(content, str):
                        try:
                            raw_data = json.loads(content)
                        except json.JSONDecodeError:
                            raw_data = content # Return as string if not JSON
                    else:
                        raw_data = content
                    break
                except Exception:
                    pass
        
        return ChatResponse(answer=answer, data=raw_data, thread_id=thread_id)
        
    except Exception as e:
        print(f"Error during chat processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
