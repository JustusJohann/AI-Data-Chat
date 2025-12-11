# Architecture Summary

This application is a **Full-Stack AI Data Analyst** that allows users to ask natural language questions about their data. It translates those questions into SQL queries, executes them against a database, and returns the results.

Here is the detailed breakdown of how it is built.

## 1. Broad Architecture Overview

The app follows a modern client-server architecture:

*   **Frontend (Next.js)**: Runs on `localhost:3000`. It provides a chat interface where users type questions. It sends these messages to the backend API.
*   **Backend (FastAPI)**: Runs on `localhost:8000`. It hosts the AI Agent. When it receives a message, it spins up the agent to reason about the request and fetch data.
*   **Database Integration (MCP)**: Instead of hardcoding database logic, the backend uses the **Model Context Protocol (MCP)** to connect to a separate "Context Server" that exposes the database as a set of tools (functions) the AI can use.

---

## 2. Backend & Agent Deep Dive

The core intelligence lies in `backend/app`. It uses **LangGraph** (a library for building stateful, multi-actor agents) and **MCP** (standard for connecting AI models to data).

### A. The Agent (`backend/app/agent.py`)

The agent is designed as a **State Graph**. This means it operates in a loop, moving between "thinking" and "acting" until it solves the problem.

1.  **The "Brain" (LLM)**:
    *   It uses **ChatGroq** (configured for models like `openai/gpt-oss-20b` or `llama-3.3-70b-versatile`) as the underlying Large Language Model.
    *   The LLM is "bound" with a specific set of tools. This means the model knows it *can* call these functions if it needs to.

2.  **The Workflow (Graph)**:
    The agent follows a circular flow defined in `create_agent_graph`:
    *   **Start**: The user's message enters the graph.
    *   **Node: `agent`**: The LLM analyzes the message. It decides whether to (a) answer directly or (b) call a tool (like `sql_query`).
    *   **Conditional Edge**:
        *   If the LLM wants to use a tool -> Go to **`tools` node**.
        *   If the LLM has the answer -> **End**.
    *   **Node: `tools`**: The system executes the requested tool (e.g., runs the SQL query) and feeds the result back to the agent.
    *   **Loop**: The agent sees the tool output and decides what to do next (e.g., "Oh, that failed, let me retry" or "Here is the data").

3.  **System Prompt**:
    The agent is given strict instructions to behave like a Data Analyst:
    *   *Investigate* (check schema first) -> *Query* -> *Refine* (fix errors) -> *Answer*.

### B. The Tool/Context Provider (`backend/app/mcp_client.py`)

This is the most unique part of the setup. The agent doesn't have SQL code inside it. Instead, it talks to an **MCP Server**.

1.  **MCP Client**:
    *   Your Python backend acts as a *Client*.
    *   When the app starts (`lifespan` in `main.py`), it spawns a subprocess: `node .../postgres-context-server/index.mjs`.
    *   This Node.js process manages the actual connection to the PostgreSQL database.

2.  **Dynamic Tool Loading**:
    *   The Python client asks the Node.js server: *"What tools do you have?"*
    *   The Node.js server replies: *"I have generic tools to list tables and run read-only SQL."*
    *   The Python client automatically converts these MCP tools into **LangChain StructuredTools** that the Python agent can understand and use.

This abstraction enables flexibility, allowing the agent to connect to different data sources (filesystems, Slack, etc.) by simply swapping the MCP server, without changing the agent's core logic.

## 3. Execution Flow

Example: When a user asks "How many users signed up yesterday?":

1.  **Frontend** sends `POST /api/chat` with the message.
2.  **FastAPI** endpoint starts the LangGraph workflow (`agent_graph.ainvoke`).
3.  **Agent Node**: The LLM sees the question. It decides it needs to know the table structure first. It calls the `list_tables` tool (provided by MCP).
4.  **Tools Node**: The request is sent to the Node.js subprocess via MCP. The Node.js script queries Postgres and returns the schema.
5.  **Agent Node**: The LLM sees the schema. It writes a SQL query: `SELECT count(*) FROM users WHERE ...`. It calls the `query` tool.
6.  **Tools Node**: Executes the SQL via MCP and returns the number (e.g., "42").
7.  **Agent Node**: Says "42 users signed up yesterday."
8.  **Backend** returns this final text + any raw data to the frontend for display.
