# Configuration settings for the MCP
class MCPSettings:
    LLM_MODEL_NAME: str = "gemini-pro" # Default LLM for general tasks

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
    ACTIVE_ROO_CODE_LLM: str = "gemini-pro" # This would be the actual model name if fetched