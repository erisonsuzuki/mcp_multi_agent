from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI
from aula 4.mcp.config.llm_config import LLMConfig # Import LLMConfig

class PromptIngestion:
    def __init__(self, llm_type: str = "Gemini"): # Use LLM type for initialization
        self.llm = ChatGoogleGenerativeAI(model=LLMConfig.get_llm_model_name(llm_type))
        self.prompt_template = PromptTemplate(
            input_variables=["prompt"],
            template="""
            You are an AI assistant designed to understand user requests and extract their intent and relevant entities.
            Your output should be a JSON object with the following structure:
            {{
              "intent": "main_goal_of_the_request",
              "entities": {{
                "entity_name_1": "entity_value_1",
                "entity_name_2": "entity_value_2"
              }},
              "original_prompt": "The original user prompt"
            }}

            Here are some examples:
            User: "Please create a python file named my_app.py"
            Output: {{ "intent": "create_file", "entities": {{ "filename": "my_app.py", "language": "python" }}, "original_prompt": "Please create a python file named my_app.py" }}

            User: "Refactor the `calculate_total` function in `src/utils.py`"
            Output: {{ "intent": "refactor_code", "entities": {{ "function_name": "calculate_total", "file_path": "src/utils.py" }}, "original_prompt": "Refactor the `calculate_total` function in `src/utils.py`" }}

            User: "{prompt}"
            Output:
            """
        )
        self.llm_chain = LLMChain(prompt=self.prompt_template, llm=self.llm)

    def ingest_prompt(self, prompt: str) -> dict:
        """
        Ingests a raw user prompt and extracts its intent and entities using an LLM.

        Args:
            prompt (str): The raw user prompt.

        Returns:
            dict: A structured dictionary containing the intent, entities, and original prompt.
        """
        try:
            response = self.llm_chain.run(prompt=prompt)
            # Attempt to parse the response as JSON.
            # The LLM is prompted to output JSON, but robust parsing is needed.
            import json
            return json.loads(response)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from LLM response: {e}")
            print(f"LLM Response: {response}")
            # Fallback or error handling if LLM doesn't return valid JSON
            return {
                "intent": "unknown",
                "entities": {},
                "original_prompt": prompt,
                "error": "JSON parsing failed"
            }
        except Exception as e:
            print(f"An unexpected error occurred during prompt ingestion: {e}")
            return {
                "intent": "unknown",
                "entities": {},
                "original_prompt": prompt,
                "error": str(e)
            }

if __name__ == "__main__":
    # Example Usage
    ingestor = PromptIngestion()
    test_prompt_1 = "Create a new HTML file called 'index.html' with a basic structure."
    result_1 = ingestor.ingest_prompt(test_prompt_1)
    print(f"Result 1: {result_1}")

    test_prompt_2 = "I need to debug the login issue in `auth.js`."
    result_2 = ingestor.ingest_prompt(test_prompt_2)
    print(f"Result 2: {result_2}")

    test_prompt_3 = "Just a simple query."
    result_3 = ingestor.ingest_prompt(test_prompt_3)
    print(f"Result 3: {result_3}")