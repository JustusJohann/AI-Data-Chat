import os
import asyncio
import shutil
from typing import Any, Dict, List, Optional, Type
from contextlib import AsyncExitStack

from pydantic import BaseModel, create_model, Field

from backend.app.logger import logger

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_core.tools import StructuredTool


class MCPClientManager:
    """
    Manages the connection to the MCP server (@zeddotdev/postgres-context-server)
    and exposes its tools as LangChain StructuredTools.
    """
    def __init__(self):
        self._session: Optional[ClientSession] = None
        self._exit_stack: Optional[AsyncExitStack] = None
        self._server_params: Optional[StdioServerParameters] = None

    async def connect(self):
        """
        Starts the MCP server via npx and establishes a session.
        """
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise ValueError("DATABASE_URL must be set in .env")

        # Ensure node is available
        node_path = shutil.which("node")
        if not node_path:
            raise RuntimeError("node not found in PATH")

        # Define server parameters
        # We pass the DATABASE_URL as an environment variable to the subprocess
        env = os.environ.copy()
        env["DATABASE_URL"] = db_url
        env["NODE_TLS_REJECT_UNAUTHORIZED"] = "0"

        # Path to the MCP server script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, "../../.."))
        script_path = os.path.join(project_root, "node_modules", "@zeddotdev", "postgres-context-server", "index.mjs")
        
        if not os.path.exists(script_path):
             # Fallback: maybe we are running in a container or different structure
             # Try simple relative path
             script_path = "node_modules/@zeddotdev/postgres-context-server/index.mjs"

        print(f"MCP Client connecting using script: {script_path}")

        self._server_params = StdioServerParameters(
            command=node_path,
            args=[script_path],
            env=env
        )

        self._exit_stack = AsyncExitStack()
        
        # Connect to the stdio server
        read, write = await self._exit_stack.enter_async_context(
            stdio_client(self._server_params)
        )
        
        # Create the session
        self._session = await self._exit_stack.enter_async_context(
            ClientSession(read, write)
        )
        
        # Initialize the session
        await self._session.initialize()
        
        print("Connected to MCP Server: @zeddotdev/postgres-context-server")

    def _create_args_schema(self, tool_name: str, schema: Dict[str, Any]) -> Type[BaseModel]:
        """
        Dynamically creates a Pydantic model from a JSON schema.
        """
        fields = {}
        if not schema or "properties" not in schema:
            return create_model(f"{tool_name}Schema")

        required = schema.get("required", [])
        
        for prop_name, prop_def in schema["properties"].items():
            prop_type = prop_def.get("type", "string")
            description = prop_def.get("description", "")
            
            # Simple type mapping
            python_type = Any
            if prop_type == "integer":
                python_type = int
            elif prop_type == "boolean":
                python_type = bool
            elif prop_type == "number":
                python_type = float
            elif prop_type == "array":
                python_type = List[Any]
            elif prop_type == "object":
                python_type = Dict[str, Any]
            else:
                python_type = str
            
            # Determine default value
            if prop_name in required:
                default = ...
            else:
                default = None
                python_type = Optional[python_type]

            fields[prop_name] = (python_type, Field(default=default, description=description))
        
        return create_model(f"{tool_name}Schema", **fields)

    async def get_tools(self) -> List[StructuredTool]:
        """
        Fetches tools from the MCP server and wraps them as LangChain StructuredTools.
        """
        if not self._session:
            raise RuntimeError("MCP Client is not connected. Call connect() first.")

        mcp_tools = await self._session.list_tools()
        langchain_tools = []

        for tool in mcp_tools.tools:
            # Capture tool_name and inputSchema appropriately
            tool_name = tool.name
            tool_schema = tool.inputSchema

            async def _create_tool_wrapper(t_name: str):
                async def _tool_wrapper(**kwargs: Any) -> Any:
                    if not self._session:
                        logger.error("MCP session disconnected. Cannot execute tool.")
                        return "Error: MCP session disconnected. Cannot execute tool."
                    try:
                        # Ensure we pass arguments as a dictionary
                        result = await self._session.call_tool(t_name, arguments=kwargs)
                        
                        # Extract text content if possible
                        if result.content and len(result.content) > 0 and hasattr(result.content[0], 'text'):
                            return result.content[0].text
                        return result.content
                    except Exception as e:
                        logger.error(f"Error executing tool {t_name}: {str(e)}", exc_info=True)
                        return f"Error executing tool {t_name}: {str(e)}"
                return _tool_wrapper

            func = await _create_tool_wrapper(tool_name)
            
            # Create Pydantic model for arguments
            args_schema = self._create_args_schema(tool_name, tool_schema)

            # Create StructuredTool
            lc_tool = StructuredTool.from_function(
                func=None,
                coroutine=func,
                name=tool_name,
                description=tool.description or f"Tool {tool_name}",
                args_schema=args_schema,
            )
            
            langchain_tools.append(lc_tool)

        return langchain_tools
        
    async def cleanup(self):
        """
        Closes the session and terminates the subprocess.
        """
        if self._exit_stack:
            await self._exit_stack.aclose()
        self._session = None
        print("MCP Client disconnected")

# Singleton instance
mcp_client = MCPClientManager()
