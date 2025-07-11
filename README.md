# Master Control Program (MCP)

This directory contains the implementation of the Master Control Program (MCP) based on the architectural design outlined in [`mcp_architecture.md`](aula%204/mcp_architecture.md). The MCP is designed to act as an orchestrator, breaking down user prompts into actionable tasks and delegating them to specialized agents (Roo Modes) using LangChain.

## Project Structure

```
mcp/
    ├── __init__.py
    ├── core/
    │   ├── __init__.py
    │   ├── prompt_ingestion.py       # Handles user prompt analysis
    │   ├── task_decomposition.py     # Breaks down requests into subtasks
    │   ├── agent_router.py           # Routes tasks to Roo Modes and suggests LLMs
    │   └── orchestration_engine.py   # Orchestrates task execution and simulates mode switching
    ├── agents/
    │   └── __init__.py               # Placeholder for future agent-specific logic
    └── config/
        ├── __init__.py
        ├── settings.py               # General MCP settings and LLM type recommendations
        └── llm_config.py             # Centralized LLM model configurations (model names, API keys)
└── README.md                     # This file
```

## Setup and Installation

1.  **Python Environment**: Ensure you have Python 3.9+ installed.
2.  **Dependencies**: Install the required Python packages. You can create a `requirements.txt` file with the following content and then install them:

    ```
    langchain
    langchain-google-genai
    # Add other necessary LangChain integrations if using different LLMs (e.g., openai, anthropic)
    ```

    Then run:
    ```bash
    pip install -r requirements.txt
    ```

3.  **API Keys**: The LLM models require API keys. It is highly recommended to set these as environment variables.
    *   For Google Gemini models, set `GOOGLE_API_KEY`.
    *   For OpenAI models (if used), set `OPENAI_API_KEY`.
    *   For Anthropic Claude models (if used), set `ANTHROPIC_API_KEY`.

    Example (for Linux/macOS):
    ```bash
    export GOOGLE_API_KEY="your_google_api_key_here"
    # export OPENAI_API_KEY="your_openai_api_key_here"
    # export ANTHROPIC_API_KEY="your_anthropic_api_key_here"
    ```
    Replace `"your_google_api_key_here"` with your actual API key.

## How to Use

The MCP is designed to be integrated into the 'roo code' VS Code extension environment. For demonstration purposes, each core module (`prompt_ingestion.py`, `task_decomposition.py`, `orchestration_engine.py`) contains an `if __name__ == "__main__":` block with example usage.

To see the MCP in action, you can run the `orchestration_engine.py` script directly:

```bash
python mcp/core/orchestration_engine.py
```

Alternatively, you can run it using Docker for a consistent environment.

### Running with Docker

1.  **Build the Docker image**: Navigate to the `aula 4/mcp/` directory in your terminal and build the image.
    ```bash
    cd mcp/
    docker build -t mcp-orchestrator .
    ```
2.  **Run the Docker container**:
    ```bash
    docker run -e GOOGLE_API_KEY="your_google_api_key_here" mcp-orchestrator
    ```
    **Important**: Replace `"your_google_api_key_here"` with your actual Google API key. If you are using other LLMs (OpenAI, Anthropic), ensure you pass their respective API keys as environment variables (e.g., `-e OPENAI_API_KEY="..."`).

This will simulate the end-to-end flow:
1.  **Prompt Ingestion**: An example user prompt is processed to extract intent and entities.
2.  **Task Decomposition**: The request is broken down into a list of subtasks.
3.  **Agent Routing**: Each subtask is routed to a suitable Roo Mode (e.g., 'code', 'architect').
4.  **Orchestration**: The `OrchestrationEngine` simulates delegating tasks to the respective Roo Modes using a mock `switch_mode` tool.

You will see console output demonstrating the flow, including the simulated mode switches and the recommended LLM for each task.

## Key Features

*   **Modular Design**: Clear separation of concerns into distinct modules.
*   **LangChain Integration**: Leverages LangChain for LLM interactions, agentic behavior, and orchestration.
*   **Dynamic Task Decomposition**: LLM-powered agents break down complex requests into manageable subtasks.
*   **Intelligent Agent Routing**: Routes tasks to the most appropriate Roo Mode based on their `Role Definition`.
*   **LLM Recommendation**: Suggests the best LLM type (e.g., Gemini, Claude, GPT-4) for each specific task based on its characteristics, as configured in `config/settings.py` and `config/llm_config.py`.
*   **Centralized LLM Configuration**: `config/llm_config.py` provides a single place to manage LLM model names and API key environment variables.

## LLM Recommendation Logic

The MCP recommends LLMs based on a mapping defined in `config/settings.py`. This mapping associates task types (e.g., `code.generate`, `design.architecture`) with conceptual LLM strengths:

*   **Gemini**: Best for creative tasks, comparative analysis, and general-purpose tasks.
*   **ChatGPT/GPT-4**: Ideal for structured sections and conversation starters.
*   **Claude**: Strong in reasoning frameworks and handling longer contexts.
*   **Others**: A fallback for tasks that don't require specific LLM strengths, defaulting to a general-purpose model.

The `config/llm_config.py` then maps these conceptual types to actual model names (e.g., "Gemini" maps to "gemini-pro" by default, but can be configured to "gemini-1.5-pro" or "gemini-1.5-flash").

## Future Enhancements

*   **Direct VS Code Integration**: Implement actual `switch_mode` calls and receive real task completion signals from the VS Code extension.
*   **Active LLM Retrieval**: Develop an API or mechanism to fetch the currently active LLM model within the Roo Code VS Code environment.
*   **Advanced Error Handling**: More robust error recovery and retry mechanisms.
*   **Persistent State**: Implement a way to save and load the MCP's state and task progress.
*   **User Interface Feedback**: Provide more detailed feedback to the user through the VS Code UI during orchestration.

## Exposing MCP as a Roo MCP Server

The current MCP implementation is a set of Python modules designed for demonstration and simulation. To allow Roo Code to connect to this MCP as a server and utilize its capabilities (e.g., for prompt ingestion, task decomposition, agent routing), additional steps are required to transform it into a functional server that adheres to the Model Context Protocol (MCP).

There are two primary ways to expose this MCP as a server:

### 1. As a Local (Stdio) Server

This is the recommended approach for locally running tools. Roo Code manages the lifecycle of the server, running it as a background process and communicating with it via standard input/output (stdio).

Here's a conceptual outline for adapting this project to a local Stdio server:

1.  **Install MCP SDK for Python (if available)**:
    *   If a Python version of `@modelcontextprotocol/sdk` exists, you would install it. Otherwise, you'd need to implement the Stdio transport logic manually (reading from stdin, writing to stdout).

2.  **Create a Server Entry Point**:
    *   Create a new Python script (e.g., `mcp/server.py`) that initializes the MCP components and exposes their functionalities as tools.

3.  **Define Tools**:
    *   Use the MCP SDK's `Tool` or a custom mechanism to define the MCP's capabilities (e.g., `ingest_prompt`, `decompose_task`, `route_task`, `execute_plan`) as callable functions.

4.  **Implement Stdio Transport**:
    *   The server script would continuously read incoming messages from `stdin`, process them, and write responses to `stdout`. This is the core of the Stdio transport.

### 2. As a Remote (HTTP/SSE) Server

This approach involves running the MCP as a standalone web server, which Roo Code connects to via HTTP. This is suitable if you want to run the MCP on a different machine or as a separate, long-running service.

Here's a conceptual outline of how this could be achieved:

1.  **Implement a Web Server**:
    *   Introduce a web framework like Flask or FastAPI to create HTTP endpoints.
    *   Example: `pip install flask` or `pip install fastapi uvicorn`.

2.  **Define MCP Endpoints**:
    *   Expose endpoints that conform to the MCP specification. The `mcp_architecture.md` mentions `/mcp/delegate`. You would also need endpoints for tool discovery (e.g., `/mcp/tools`) and potentially resource access.
    *   These endpoints would internally call the `PromptIngestion`, `TaskDecomposition`, and `AgentRouter` components.

3.  **Tool Registration**:
    *   The MCP server would need to define its own capabilities (e.g., "ingest_prompt", "decompose_task", "route_task", "execute_plan") as tools that Roo can discover and use. This would involve returning a structured list of tools via a dedicated endpoint.

4.  **Dockerfile Update**:
    *   Modify the `Dockerfile` to run the web server application (e.g., `CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]` if using FastAPI).
    *   Ensure the Docker container exposes the necessary port (e.g., `EXPOSE 8000`).

**Example Conceptual `main.py` (using FastAPI):**

```python
# mcp/main.py (Conceptual)
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any

from mcp.core.prompt_ingestion import PromptIngestion
from mcp.core.task_decomposition import TaskDecomposition
from mcp.core.agent_router import AgentRouter, get_available_roo_modes
from mcp.core.orchestration_engine import OrchestrationEngine
from mcp.config.settings import MCPSettings
from mcp.config.llm_config import LLMConfig

app = FastAPI()

# Initialize MCP components
prompt_ingestor = PromptIngestion(llm_type=MCPSettings.LLM_MODEL_NAME)
task_decomposer = TaskDecomposition(llm_type=MCPSettings.LLM_MODEL_NAME)
agent_router = AgentRouter(llm_model_name=LLMConfig.get_llm_model_name(MCPSettings.LLM_MODEL_NAME))
orchestration_engine = OrchestrationEngine(default_llm_type=MCPSettings.LLM_MODEL_NAME)

class PromptRequest(BaseModel):
    prompt: str

class TaskRequest(BaseModel):
    request: Dict[str, Any]

class ExecutePlanRequest(BaseModel):
    tasks: List[Dict[str, Any]]

@app.post("/mcp/ingest_prompt")
async def ingest_prompt_endpoint(request: PromptRequest):
    """Endpoint to ingest and analyze a user prompt."""
    result = prompt_ingestor.ingest_prompt(request.prompt)
    return {"status": "success", "data": result}

@app.post("/mcp/decompose_task")
async def decompose_task_endpoint(request: TaskRequest):
    """Endpoint to decompose a structured request into subtasks."""
    # In a real scenario, available_tools would be dynamically fetched or passed
    available_tools = get_available_roo_modes() # Using the same mock for now
    tasks = task_decomposer.decompose_request(request.request, available_tools)
    return {"status": "success", "data": tasks}

@app.post("/mcp/route_task")
async def route_task_endpoint(request: TaskRequest):
    """Endpoint to route a single task to the best Roo Mode."""
    routed_info = agent_router.route_task(request.request)
    return {"status": "success", "data": routed_info}

@app.post("/mcp/execute_plan")
async def execute_plan_endpoint(request: ExecutePlanRequest):
    """Endpoint to execute a plan of tasks."""
    overall_result = orchestration_engine.execute_plan(request.tasks)
    return {"status": "success", "data": overall_result}

@app.get("/mcp/tools")
async def get_mcp_tools():
    """Endpoint to list the tools provided by this MCP server."""
    # This would describe the capabilities of this MCP itself, not Roo's modes.
    # For example, it could expose 'ingest_prompt', 'decompose_task', 'route_task', 'execute_plan'
    return {
        "tools": [
            {"name": "ingest_prompt", "description": "Ingests a raw user prompt and extracts intent/entities."},
            {"name": "decompose_task", "description": "Decomposes a structured request into subtasks."},
            {"name": "route_task", "description": "Routes a single task to the most suitable Roo Mode."},
            {"name": "execute_plan", "description": "Executes a plan of tasks by delegating to Roo Modes."}
        ]
    }

# To run this conceptual server (after installing fastapi and uvicorn):
# uvicorn mcp.main:app --host 0.0.0.0 --port 8000
```

## Configuring Roo Code to use the MCP Server

To enable Roo Code to connect to the local MCP server you just created, you need to add its configuration to the `mcp_settings.json` file.

1.  **Locate `mcp_settings.json`**:
    *   On Linux, this file is typically located at: `/home/sony/.vscode-server/data/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json`

2.  **Add the Server Configuration**:
    *   Open the `mcp_settings.json` file.
    *   Inside the `"mcpServers"` object, add a new entry for `"roo-mcp-server"`. Ensure you replace the placeholder path with the actual path to your `index.js` file.

    ```json
    {
        "mcpServers": {
            "github": {
                "command": "docker",
                "args": [
                    "run",
                    "-i",
                    "--rm",
                    "-e",
                    "GITHUB_PERSONAL_ACCESS_TOKEN",
                    "-e",
                    "GITHUB_TOOLSETS",
                    "-e",
                    "GITHUB_READ_ONLY",
                    "ghcr.io/github/github-mcp-server"
                ],
                "env": {
                    "GITHUB_PERSONAL_ACCESS_TOKEN": "your_github_token",
                    "GITHUB_TOOLSETS": "",
                    "GITHUB_READ_ONLY": ""
                }
            },
            "roo-mcp-server": {
                "command": "node",
                "args": ["/home/sony/www/ia/mcp/server/build/index.js"],
                "disabled": false,
                "alwaysAllow": [],
                "disabledTools": []
            }
        }
    }
    ```
    *   **Justification**: This configuration tells Roo Code how to start and communicate with your local MCP server.
        *   `"command": "node"`: Specifies that the server should be run using Node.js.
        *   `"args": ["/home/sony/www/ia/mcp/server/build/index.js"]`: Provides the full path to the compiled JavaScript entry point of your MCP server.
        *   `"disabled": false`: Ensures the server is active and enabled.
        *   `"alwaysAllow": []` and `"disabledTools": []`: These are default settings, indicating no tools are always allowed without confirmation and no tools are explicitly disabled.

3.  **Save the File**:
    *   Save the `mcp_settings.json` file. Roo Code will automatically detect the changes and attempt to connect to the new server.

Once configured, Roo Code will recognize the `roo-mcp-server` and its exposed tools (like `greet`). You can then interact with these tools directly through your prompts.
```