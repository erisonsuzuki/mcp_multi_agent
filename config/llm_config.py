import os

class LLMConfig:
    """
    Configuration for various LLM models, including their specific model names
    and a placeholder for API keys (which should ideally come from environment variables).
    """

    # Gemini Models
    GEMINI_PRO = {
        "model_name": "gemini-pro",
        "api_key_env_var": "GOOGLE_API_KEY",
        "description": "Google Gemini Pro: Good for general tasks, creative content, and comparative analysis."
    }
    GEMINI_1_5_PRO = {
        "model_name": "gemini-1.5-pro",
        "api_key_env_var": "GOOGLE_API_KEY",
        "description": "Google Gemini 1.5 Pro: Enhanced capabilities for complex reasoning and larger contexts."
    }
    GEMINI_1_5_FLASH = {
        "model_name": "gemini-1.5-flash",
        "api_key_env_var": "GOOGLE_API_KEY",
        "description": "Google Gemini 1.5 Flash: Optimized for speed and efficiency, suitable for quick tasks."
    }

    # OpenAI Models (placeholders)
    GPT_4 = {
        "model_name": "gpt-4",
        "api_key_env_var": "OPENAI_API_KEY",
        "description": "OpenAI GPT-4: Excellent for structured sections and conversation starters."
    }
    GPT_3_5_TURBO = {
        "model_name": "gpt-3.5-turbo",
        "api_key_env_var": "OPENAI_API_KEY",
        "description": "OpenAI GPT-3.5 Turbo: Cost-effective and fast for many common tasks."
    }

    # Anthropic Claude Models (placeholders)
    CLAUDE_3_OPUS = {
        "model_name": "claude-3-opus-20240229",
        "api_key_env_var": "ANTHROPIC_API_KEY",
        "description": "Anthropic Claude 3 Opus: Strong reasoning frameworks and longer context windows."
    }
    CLAUDE_3_SONNET = {
        "model_name": "claude-3-sonnet-20240229",
        "api_key_env_var": "ANTHROPIC_API_KEY",
        "description": "Anthropic Claude 3 Sonnet: Balanced performance for general AI tasks."
    }

    # Mapping from conceptual LLM types (used in settings.py) to actual model configurations
    LLM_TYPE_TO_CONFIG = {
        "Gemini": GEMINI_PRO, # Default Gemini model for general "Gemini" type tasks
        "ChatGPT/GPT-4": GPT_4,
        "Claude": CLAUDE_3_OPUS,
        "Others": GEMINI_PRO # Fallback for "Others" or unspecific types
    }

    @staticmethod
    def get_llm_model_name(llm_type: str) -> str:
        """
        Returns the specific model name for a given conceptual LLM type.
        """
        config = LLMConfig.LLM_TYPE_TO_CONFIG.get(llm_type, LLMConfig.GEMINI_PRO)
        return config["model_name"]

    @staticmethod
    def get_api_key(llm_type: str) -> str:
        """
        Returns the API key from environment variables for a given conceptual LLM type.
        """
        config = LLMConfig.LLM_TYPE_TO_CONFIG.get(llm_type, LLMConfig.GEMINI_PRO)
        api_key_env_var = config["api_key_env_var"]
        return os.getenv(api_key_env_var, "") # Return empty string if not found

    @staticmethod
    def get_llm_description(llm_type: str) -> str:
        """
        Returns the description for a given conceptual LLM type.
        """
        config = LLMConfig.LLM_TYPE_TO_CONFIG.get(llm_type, LLMConfig.GEMINI_PRO)
        return config["description"]

# Example usage (for testing purposes)
if __name__ == "__main__":
    print(f"Gemini model name: {LLMConfig.get_llm_model_name('Gemini')}")
    print(f"GPT-4 model name: {LLMConfig.get_llm_model_name('ChatGPT/GPT-4')}")
    print(f"Claude model name: {LLMConfig.get_llm_model_name('Claude')}")
    print(f"Description for Gemini: {LLMConfig.get_llm_description('Gemini')}")
    print(f"API Key Env Var for Gemini: {LLMConfig.GEMINI_PRO['api_key_env_var']}")