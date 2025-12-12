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

Follow these instructions to set up the project on your local machine.

### Prerequisites

Ensure you have the following installed:

1.  **Git**: [Download Git](https://git-scm.com/downloads)
2.  **PostgreSQL**: Ensure your database is running and accessible.

#### Installing Node.js (via nvm)
We recommend using `nvm` (Node Version Manager) to install Node.js.

1.  **Install nvm**:
    ```bash
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
    ```
    *Restart your terminal after installation.*

2.  **Install Node.js 18+**:
    ```bash
    nvm install 18
    nvm use 18
    ```

#### Installing Python 3.10+
You need Python 3.10 or higher.
- **macOS (via Homebrew)**: `brew install python`
- **Windows**: [Download from Python.org](https://www.python.org/downloads/)
- **Linux**: `sudo apt install python3 python3-venv`

---

### Installation

#### 1. Clone the Repository
```bash
git clone <repository_url>
cd <repository_name>
```

#### 2. Backend Setup
Set up the Python environment in the **root** of the project.

1.  **Create a Virtual Environment**:
    ```bash
    python -m venv .venv
    ```

2.  **Activate the Environment**:
    - macOS/Linux:
      ```bash
      source .venv/bin/activate
      ```
    - Windows:
      ```bash
      .venv\Scripts\activate
      ```

3.  **Install Dependencies**:
    ```bash
    pip install -r backend/requirements.txt
    ```

4.  **Install Root Node Dependencies (for MCP)**:
    Required for the PostreSQL Context Server.
    ```bash
    npm install
    ```

5.  **Environment Configuration**:
    Create a `.env` file in the **root** directory (same level as `start_app.sh`).
    
    ```bash
    touch .env
    ```

    Add the following content to `.env` (adjust values as needed):
    ```env
    # Database Connection String
    DATABASE_URL=postgresql://user:password@localhost:5432/your_database_name

    # LLM API Keys
    GROQ_API_KEY=your_groq_api_key_here
    # Optional: OPENAI_API_KEY=your_openai_key_here
    ```

#### 3. Frontend Setup

1.  **Navigate to Frontend**:
    ```bash
    cd frontend
    ```

2.  **Install Dependencies**:
    ```bash
    npm install
    ```

3.  **Return to Root**:
    ```bash
    cd ..
    ```

---

### Running the Application

You can start the application using the helper script or manually.

#### Option A: Quick Start (Recommended)
We have provided a script that starts both the backend and frontend in parallel.

Make sure you are in the project root and run:
```bash
./start_app.sh
```
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000

#### Option B: Manual Start

**1. Start Backend**
Open a terminal in the project root:
```bash
source .venv/bin/activate
python -m uvicorn backend.app.main:app --reload --port 8000
```
*Wait for the message "Application startup complete".*

**2. Start Frontend**
Open a **new** terminal window:
```bash
cd frontend
npm run dev
```

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
