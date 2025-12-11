import asyncio
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

# Add the project root to sys.path so we can import backend.app modules
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from backend.app.mcp_client import mcp_client
from backend.app.agent import create_agent_graph

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

async def main():
    print("Initializing MCP Client...")
    try:
        await mcp_client.connect()
    except Exception as e:
        print(f"Failed to connect to MCP server: {e}")
        return

    try:
        print("Fetching tools...")
        tools = await mcp_client.get_tools()
        
        print("Creating Agent Graph...")
        graph = create_agent_graph(tools)
        
        print("\n=== Natural Language Data Analyst CLI ===")
        print("Type 'exit' or 'quit' to stop.")
        print("=========================================\n")
        
        while True:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit"]:
                break
            
            print("Agent: Thinking...")
            
            try:
                # We retain history by passing the previous state? 
                # For this simple CLI, let's just make each query independent or we could maintain a conversation list.
                # However, the graph logic in `agent.py` takes a list of messages.
                # If we want memory, we should keep a list of messages outside.
                
                # Let's simple keep a running list of messages for this session
                # But creating a new graph run each time might clear it depending on how checkpointer is used.
                # Since we didn't add a checkpointer, we pass the full state.
                
                # Actually, effectively we are stateless between turns unless we feed the output back.
                # Let's do a simple one-shot for now, or accumulate if we want. 
                # The user request implies "The app allows users to ask questions", often follow-ups.
                # Let's accumulate messages.
                
                # Wait, if I reuse `messages` list, I need to handle `add_messages` reducer manually?
                # Using ainivoke returns the FINAL state.
                # So I can just take the output state and use it as input for the next turn.
                
                # Initial state for first turn
                if 'conversational_state' not in locals():
                    conversational_state = {"messages": []}
                
                conversational_state["messages"].append(HumanMessage(content=user_input))
                
                result = await graph.ainvoke(conversational_state)
                
                # Update state for next turn
                conversational_state = result
                
                # Print the last message (AI response)
                last_msg = result["messages"][-1]
                print(f"\nAgent: {last_msg.content}\n")
                
            except Exception as e:
                print(f"Error: {e}")

    finally:
        await mcp_client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
