import json
import os

# Configuration settings for the MCP
class MCPSettings:
    _config_data = {}
    _config_file_path = os.path.join(os.path.dirname(__file__), 'mcp.json')

    @classmethod
    def load_config(cls):
        if not cls._config_data:
            try:
                with open(cls._config_file_path, 'r') as f:
                    cls._config_data = json.load(f)
            except FileNotFoundError:
                print(f"Warning: {cls._config_file_path} not found. Using default settings.")
                cls._config_data = {} # Ensure it's an empty dict if file not found
            except json.JSONDecodeError:
                print(f"Error: Could not decode JSON from {cls._config_file_path}. Using default settings.")
                cls._config_data = {}

    @classmethod
    def get_default_llm_type(cls) -> str:
        cls.load_config() # Ensure config is loaded
        return cls._config_data.get("llm_config", {}).get("default_llm_type", "Gemini")

    # Default LLM for general tasks (can be overridden by mcp.json)
    LLM_MODEL_NAME: str = get_default_llm_type()

    # Mapping of task types to recommended LLM capabilities/types
    # This can be expanded with more granular task types and specific LLM recommendations
    # Based on user feedback:
    # ChatGPT/GPT-4: Structured sections, conversation starters
    # Claude: Longer context, reasoning frameworks
    # Gemini: Creative tasks, comparative analysis
    # Others: Apply universal best practices
    RECOMMENDED_LLMS_BY_TASK_TYPE = {
        "code.generate": "Gemini", # Creative tasks, good for code generation
        "code.refactor": "Gemini", # Creative tasks, good for code refactoring
        "debug.issue": "Claude", # Reasoning frameworks, good for debugging complex issues
        "design.architecture": "Claude", # Longer context, reasoning frameworks, good for architectural design
        "get.documentation": "ChatGPT/GPT-4", # Structured sections, good for information retrieval
        "file.create": "Others", # Simple task, universal best practices
        "default": "Gemini" # Fallback for unlisted task types
    }

    # Placeholder for active LLM from VS Code.
    # In a real scenario, this would be dynamically fetched from the VS Code environment.
    # For now, it can be set manually or default to LLM_MODEL_NAME.
    ACTIVE_ROO_CODE_LLM: str = get_default_llm_type() # This would be the actual model name if fetched