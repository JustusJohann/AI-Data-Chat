# AI Data Chat

A powerful **Full-Stack AI Data Analyst** that enables natural language interaction with your database. Built with **LangGraph**, **FastAPI**, **Next.js**, and the **Model Context Protocol (MCP)**.

## Features

- **Natural Language to SQL**: Ask questions in plain English (e.g., "How many users signed up yesterday?").
- **Agentic Workflow**: The AI follows a rigorous "Investigate -> Query -> Refine -> Answer" process to ensure accuracy.
- **Interactive Chat Interface**: A modern, responsive web UI built with Next.js and Tailwind CSS.
- **MCP Integration**: Uses the [Model Context Protocol](https://modelcontextprotocol.io/) to securely and dynamically interact with the database.
- **Schema Awareness**: automatically investigates database schema before querying.
- **Self-Correction**: capable of fixing its own failed queries.

## Architecture

The application is split into a Python backend (AI Brain) and a Next.js frontend (UI).

- **Backend (`/backend`)**: FastAPI server hosting the LangGraph agent. It spawns a Node.js MCP server (subprocess) to talk to PostgreSQL.
- **Frontend (`/frontend`)**: Next.js application providing the chat interface.

For a deep dive into the architecture, check out [summary.md](./summary.md).

## Tech Stack

### Backend
- **Framework**: FastAPI
- **AI/Agents**: LangGraph, LangChain
- **LLM**: Groq (Llama 3 / Mixtral) or OpenAI compatible
- **Protocol**: MCP (Model Context Protocol)
- **Database**: PostgreSQL

### Frontend
- **Framework**: Next.js 14+ (App Router)
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Markdown**: React Markdown

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL Database

### 1. Backend Setup

Navigate to the backend directory:
```bash
cd backend
```

Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Create a `.env` file in the `backend` directory:
```bash
# backend/.env
DATABASE_URL=postgresql://user:password@localhost:5432/your_db
GROQ_API_KEY=your_groq_api_key
# Optional: OPENAI_API_KEY if using OpenAI models
```

Start the server:
```bash
# Using the CLI wrapper
python cli_agent.py

# OR running the API directly
uvicorn app.main:app --reload
```
The backend API will run on `http://localhost:8000`.

### 2. Frontend Setup

Navigate to the frontend directory:
```bash
cd frontend
```

Install dependencies:
```bash
npm install
```

Start the development server:
```bash
npm run dev
```
The application will be available at `http://localhost:3000`.

## How it Works

1. **User asks a question** via the Frontend.
2. **Backend Agent** receives the message and enters a loop:
   - **Investigates** schema using MCP tools.
   - **Generates** a SQL query.
   - **Executes** the query via the MCP server.
   - **Analyzes** the results.
3. **Response** is streamed back to the user with data and insights.

## License

[MIT](LICENSE)
