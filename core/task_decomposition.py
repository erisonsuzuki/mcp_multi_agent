from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI
import json
from aula 4.mcp.config.llm_config import LLMConfig # Import LLMConfig

class TaskDecomposition:
    def __init__(self, llm_type: str = "Gemini"): # Use LLM type for initialization
        self.llm = ChatGoogleGenerativeAI(model=LLMConfig.get_llm_model_name(llm_type))
        self.prompt_template = PromptTemplate(
            input_variables=["request", "available_tools"],
            template="""
            You are an AI assistant responsible for breaking down a user's request into a sequence of smaller, executable subtasks.
            The request is provided as a JSON object containing "intent" and "entities".
            You also have a list of "available_tools" which represent the capabilities of different agents (Roo Modes).
            Your goal is to generate a list of task dictionaries, where each dictionary represents a step to be executed by a specific agent mode.
            Each task dictionary should have at least "task_type" and "params".
            The "task_type" should correspond to an action that can be performed by one of the available tools.
            The "params" should contain all necessary information for that task.

            Available Tools (Roo Modes):
            {available_tools}

            User Request:
            {request}

            Output a JSON list of task dictionaries. Ensure the output is valid JSON.

            Example Output:
            [
              {{"task_type": "file.create", "params": {{"path": "index.html", "content": "..."}}}},
              {{"task_type": "code.generate", "params": {{"target_file": "script.js", "prompt": "..."}}}}
            ]
            """
        )
        self.llm_chain = LLMChain(prompt=self.prompt_template, llm=self.llm)

    def decompose_request(self, request: dict, available_tools: list[dict]) -> list[dict]:
        """
        Decomposes a structured user request into a list of executable subtasks.

        Args:
            request (dict): The structured request from the prompt ingestion module.
            available_tools (list[dict]): A list of dictionaries describing available tools/Roo Modes.

        Returns:
            list[dict]: A list of task dictionaries.
        """
        try:
            # Convert available_tools to a string format suitable for the prompt
            tools_str = json.dumps(available_tools, indent=2)
            request_str = json.dumps(request, indent=2)

            response = self.llm_chain.run(request=request_str, available_tools=tools_str)
            return json.loads(response)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from LLM response in TaskDecomposition: {e}")
            print(f"LLM Response: {response}")
            return [{"task_type": "error", "params": {"message": "Failed to decompose request: Invalid JSON from LLM"}}]
        except Exception as e:
            print(f"An unexpected error occurred during task decomposition: {e}")
            return [{"task_type": "error", "params": {"message": f"Failed to decompose request: {str(e)}"}}]

if __name__ == "__main__":
    # Example Usage
    decomposer = TaskDecomposition()

    # Mock available tools (Roo Modes)
    mock_available_tools = [
        {"name": "code", "description": "Generates, debugs, and refactors code.", "slug": "code"},
        {"name": "architect", "description": "Handles design and planning tasks.", "slug": "architect"},
        {"name": "file_manager", "description": "Creates, reads, updates, and deletes files.", "slug": "file_manager"}
    ]

    # Mock request from PromptIngestion
    mock_request_1 = {
        "intent": "create_file",
        "entities": {
            "filename": "app.js",
            "language": "javascript",
            "content_description": "a simple 'Hello World' script"
        },
        "original_prompt": "Create a javascript file named app.js with a simple 'Hello World' script."
    }

    print("Decomposing Request 1:")
    tasks_1 = decomposer.decompose_request(mock_request_1, mock_available_tools)
    print(f"Tasks 1: {tasks_1}")

    mock_request_2 = {
        "intent": "refactor_code",
        "entities": {
            "function_name": "process_data",
            "file_path": "src/data_utils.py"
        },
        "original_prompt": "Refactor the `process_data` function in `src/data_utils.py` for better performance."
    }

    print("\nDecomposing Request 2:")
    tasks_2 = decomposer.decompose_request(mock_request_2, mock_available_tools)
    print(f"Tasks 2: {tasks_2}")