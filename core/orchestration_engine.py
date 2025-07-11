from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI # Import here for dynamic model loading
import json

from mcp.config.settings import MCPSettings
from mcp.config.llm_config import LLMConfig # Import LLMConfig
from mcp.core.agent_router import get_available_roo_modes, AgentRouter

# Custom Tool for `switch_mode`
# In a real VS Code extension, this would trigger the actual VS Code command.
def _switch_mode_tool_func(mode_slug: str, message: str = "", recommended_llm_type: str = "N/A") -> str:
    """
    Simulates the `switch_mode` tool call.
    In a real environment, this would interact with the VS Code extension to change modes.
    """
    print(f"--- SIMULATING switch_mode ---")
    print(f"Switching to mode: {mode_slug}")
    print(f"Reason/Message: {message}")
    print(f"Recommended LLM for this task: {recommended_llm_type} ({LLMConfig.get_llm_description(recommended_llm_type)})")
    print(f"--- END SIMULATION ---")
    # In a real scenario, this would block until the mode completes its task and returns a result.
    # For now, we'll just return a success message.
    return f"Successfully requested mode switch to {mode_slug}. Recommended LLM: {recommended_llm_type}. Waiting for task completion..."

switch_mode_tool = Tool(
    name="switch_mode",
    func=_switch_mode_tool_func,
    description="Switches the current execution context to a different Roo Mode. "
                "Requires 'mode_slug' (e.g., 'code', 'architect'), an optional 'message' (reason for switch), "
                "and an optional 'recommended_llm_type' (suggested LLM type for the task)."
)

class OrchestrationEngine:
    def __init__(self, default_llm_type: str = "Gemini"): # Use LLM type for initialization
        self.default_llm_type = default_llm_type
        self.llm = ChatGoogleGenerativeAI(model=LLMConfig.get_llm_model_name(default_llm_type), temperature=0.2)
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.agent_router = AgentRouter(llm_model_name=LLMConfig.get_llm_model_name(default_llm_type)) # Initialize AgentRouter with default LLM

        # Get available Roo Modes and create LangChain Tools for them
        self.roo_mode_tools = self._create_roo_mode_tools()
        self.all_tools = self.roo_mode_tools + [switch_mode_tool]

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are the Master Control Program (MCP) Orchestration Engine. "
                       "Your goal is to execute a sequence of tasks by delegating them to appropriate Roo Modes. "
                       "Use the 'switch_mode' tool to delegate tasks to specific modes. "
                       "After a mode completes its task, you will receive a 'task_complete' signal (simulated). "
                       "Manage the overall workflow and aggregate results."),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])

        self.agent = create_tool_calling_agent(self.llm, self.all_tools, self.prompt)
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.all_tools,
            memory=self.memory,
            verbose=True, # Keep verbose for debugging orchestration flow
            handle_parsing_errors=True # Handle cases where LLM output is not perfectly parsable
        )

    def _create_roo_mode_tools(self) -> list[Tool]:
        """
        Creates LangChain Tool objects for each available Roo Mode,
        which will be called by the Orchestration Engine to trigger mode switches.
        """
        tools = []
        for mode in get_available_roo_modes():
            # The func for these tools will be to call the actual `switch_mode_tool`
            # with the appropriate mode slug and task details.
            def _delegate_to_mode(task_details: str, mode_slug=mode["slug"]):
                # When delegating, we need to get the recommended LLM for this specific task.
                # This requires calling the AgentRouter.
                task_dict = json.loads(task_details) # Convert task_details string back to dict
                routed_info = self.agent_router.route_task(task_dict) # Use the router to get LLM recommendation
                
                return _switch_mode_tool_func(
                    mode_slug,
                    message=f"Delegating task: {task_dict.get('task_type', 'N/A')} - {task_dict.get('params', {})}",
                    recommended_llm_type=routed_info.get("recommended_llm", "N/A")
                )

            tool = Tool(
                name=mode["slug"], # Tool name is the mode slug
                func=_delegate_to_mode,
                description=f"Delegates a task to the {mode['name']} mode. "
                            f"Role: {mode['role_definition']}. "
                            f"Input should be a JSON string describing the task for this mode."
            )
            tools.append(tool)
        return tools

    def execute_plan(self, tasks: list[dict]) -> dict:
        """
        Executes a plan of tasks by delegating to appropriate Roo Modes.

        Args:
            tasks (list[dict]): A list of task dictionaries generated by TaskDecomposition.

        Returns:
            dict: The aggregated result of all executed tasks.
        """
        final_results = {"status": "success", "results": []}
        for i, task in enumerate(tasks):
            print(f"\n--- Executing Task {i+1}/{len(tasks)}: {task.get('task_type', 'N/A')} ---")
            task_input_str = json.dumps(task)
            try:
                # The agent executor will decide which tool (Roo Mode) to call based on the task.
                # We provide the task as the input to the agent.
                # The agent's prompt will guide it to use the appropriate tool.
                result = self.agent_executor.invoke({"input": f"Execute the following task: {task_input_str}"})
                
                # In a real system, the result would come back from the switched mode.
                # Here, we're getting the output of the simulated switch_mode_tool.
                task_result = {
                    "task": task,
                    "status": "completed",
                    "output": result.get("output", "No specific output from simulated mode.")
                }
                final_results["results"].append(task_result)
                print(f"Task {i+1} completed. Output: {task_result['output']}")

                # Simulate task completion signal from the Roo Mode back to MCP
                # In a real system, this would be an external event.
                self.memory.save_context(
                    {"input": f"Task {task.get('task_type', 'N/A')} delegated to {result.get('output', 'unknown mode')}."},
                    {"output": f"Task {task.get('task_type', 'N/A')} completed successfully by {result.get('output', 'unknown mode')}."}
                )

            except Exception as e:
                print(f"Error executing task {i+1}: {e}")
                task_result = {
                    "task": task,
                    "status": "failed",
                    "error": str(e)
                }
                final_results["results"].append(task_result)
                final_results["status"] = "partial_success_with_errors"
                # Continue to next task or break, depending on error handling strategy
                break # For now, break on first error

        return final_results

if __name__ == "__main__":
    orchestrator = OrchestrationEngine()

    # Example plan (list of tasks)
    example_tasks = [
        {"task_type": "file.create", "params": {"path": "new_file.txt", "content": "Hello from MCP!"}},
        {"task_type": "code.generate", "params": {"target_file": "script.py", "prompt": "Python function to add two numbers"}},
        {"task_type": "design.architecture", "params": {"system": "User Management", "modules": ["auth", "profile"]}},
        {"task_type": "debug.issue", "params": {"file": "buggy_code.js", "description": "Infinite loop in data processing"}},
        {"task_type": "get.documentation", "params": {"topic": "LangChain Chains"}}
    ]

    print("Starting Orchestration Engine with example tasks...")
    overall_result = orchestrator.execute_plan(example_tasks)
    print("\n--- Overall Orchestration Result ---")
    print(json.dumps(overall_result, indent=2))