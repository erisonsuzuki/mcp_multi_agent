from langchain.tools import Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate
import json
from aula 4.mcp.config.settings import MCPSettings

# Placeholder for getting available Roo Modes.
# In a real scenario, this would dynamically discover modes from the VS Code environment or a config file.
def get_available_roo_modes() -> list[dict]:
    """
    Returns a list of dictionaries, each representing an available Roo Mode.
    Each dictionary should contain 'slug', 'name', and 'role_definition'.
    """
    return [
        {
            "slug": "code",
            "name": "💻 Code",
            "role_definition": "The standard 'Code' mode for generating, debugging, and refactoring code. Use this for any code-related tasks."
        },
        {
            "slug": "architect",
            "name": "🏗️ Architect",
            "role_definition": "The 'Architect' mode for design and planning tasks. Use this for high-level system design, architecture, and planning."
        },
        {
            "slug": "debug",
            "name": "🪲 Debug",
            "role_definition": "The 'Debug' mode for troubleshooting issues, investigating errors, or diagnosing problems. Use this for bug fixing and error analysis."
        },
        {
            "slug": "ask",
            "name": "❓ Ask",
            "role_definition": "The 'Ask' mode for getting explanations, documentation, or answers to technical questions. Use this when you need information or clarification."
        },
        {
            "slug": "orchestrator",
            "name": "🪃 Orchestrator",
            "role_definition": "The 'Orchestrator' mode for complex, multi-step projects that require coordination across different specialties. Use this for breaking down large tasks and managing workflows."
        }
    ]

class AgentRouter:
    def __init__(self, llm_model_name: str = MCPSettings.LLM_MODEL_NAME):
        self.llm = ChatGoogleGenerativeAI(model=llm_model_name, temperature=0) # Lower temperature for more deterministic routing
        self.roo_mode_tools = self._create_roo_mode_tools()
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert agent router. Your task is to select the most appropriate Roo Mode (tool) for a given task."),
            ("human", "Given the following task: {task}\n\nSelect the best tool from the available tools."),
            ("human", "Available tools: {tool_names}")
        ])
        self.agent = create_tool_calling_agent(self.llm, self.roo_mode_tools, self.prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.roo_mode_tools, verbose=False) # Set verbose to True for debugging

    def _create_roo_mode_tools(self) -> list[Tool]:
        """
        Creates LangChain Tool objects for each available Roo Mode.
        """
        tools = []
        for mode in get_available_roo_modes():
            # The func here is a placeholder. The actual delegation happens in the Orchestration Engine.
            # The AgentRouter's job is just to select the correct tool (mode slug).
            tool = Tool(
                name=mode["slug"],
                func=lambda x, slug=mode["slug"]: slug, # Return the slug directly
                description=mode["role_definition"]
            )
            tools.append(tool)
        return tools

    def route_task(self, task: dict) -> dict: # Changed return type to dict
        """
        Routes a given task to the most suitable Roo Mode (agent) and suggests an LLM.

        Args:
            task (dict): A dictionary representing the task to be routed.
                         Expected to have a 'task_type' and 'params' key.

        Returns:
            dict: A dictionary containing the selected mode slug and the recommended LLM type.
                  Example: {"mode_slug": "code", "recommended_llm": "Gemini"}
        """
        try:
            task_type = task.get('task_type', 'default')
            recommended_llm = MCPSettings.RECOMMENDED_LLMS_BY_TASK_TYPE.get(task_type, MCPSettings.RECOMMENDED_LLMS_BY_TASK_TYPE["default"])

            task_description = f"Task Type: {task_type}\nParams: {json.dumps(task.get('params', {}))}"
            
            result = self.agent_executor.invoke({"task": task_description, "tool_names": [tool.name for tool in self.roo_mode_tools]})
            
            selected_mode_slug = result.get("output")
            
            if selected_mode_slug and selected_mode_slug in [mode["slug"] for mode in get_available_roo_modes()]:
                return {"mode_slug": selected_mode_slug, "recommended_llm": recommended_llm}
            else:
                print(f"Agent Router failed to select a valid mode. Result: {result}")
                return {"mode_slug": "orchestrator", "recommended_llm": recommended_llm} # Fallback
        except Exception as e:
            print(f"An unexpected error occurred during agent routing: {e}")
            return {"mode_slug": "orchestrator", "recommended_llm": recommended_llm} # Fallback

if __name__ == "__main__":
    router = AgentRouter()

    # Example tasks
    task_1 = {"task_type": "code.generate", "params": {"target_file": "main.py", "prompt": "Python script for Fibonacci sequence"}}
    print(f"Routing task 1: {task_1}")
    routed_info_1 = router.route_task(task_1)
    print(f"Routed to: {routed_info_1['mode_slug']}, Recommended LLM: {routed_info_1['recommended_llm']}\n")

    task_2 = {"task_type": "design.architecture", "params": {"system_name": "E-commerce Platform", "components": ["frontend", "backend", "database"]}}
    print(f"Routing task 2: {task_2}")
    routed_info_2 = router.route_task(task_2)
    print(f"Routed to: {routed_info_2['mode_slug']}, Recommended LLM: {routed_info_2['recommended_llm']}\n")

    task_3 = {"task_type": "debug.issue", "params": {"file": "login.js", "error_message": "Authentication failed"}}
    print(f"Routing task 3: {task_3}")
    routed_info_3 = router.route_task(task_3)
    print(f"Routed to: {routed_info_3['mode_slug']}, Recommended LLM: {routed_info_3['recommended_llm']}\n")

    task_4 = {"task_type": "get.documentation", "params": {"topic": "LangChain Agents"}}
    print(f"Routing task 4: {task_4}")
    routed_info_4 = router.route_task(task_4)
    print(f"Routed to: {routed_info_4['mode_slug']}, Recommended LLM: {routed_info_4['recommended_llm']}\n")

    task_5 = {"task_type": "manage.project", "params": {"project_name": "New Feature", "steps": ["design", "implement", "test"]}}
    print(f"Routing task 5: {task_5}")
    routed_info_5 = router.route_task(task_5)
    print(f"Routed to: {routed_info_5['mode_slug']}, Recommended LLM: {routed_info_5['recommended_llm']}\n")

    task_6 = {"task_type": "unknown.task", "params": {"description": "This is an unroutable task."}}
    print(f"Routing task 6: {task_6}")
    routed_info_6 = router.route_task(task_6)
    print(f"Routed to: {routed_info_6['mode_slug']}, Recommended LLM: {routed_info_6['recommended_llm']}\n")