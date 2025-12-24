from .llm import OllamaClient
from src.utils.logger import setup_logger

logger = setup_logger("EvaluatorAgent")

class EvaluatorAgent:
    def __init__(self, model_name: str, base_url: str):
        self.model = model_name
        self.client = OllamaClient(base_url=base_url)

    def evaluate(self, input_data, output, rule):
        logger.debug(f"Evaluating input: {input_data} -> output: {output}")
        prompt = f"""
        Task: Determine if the output is correct for the given input based on the following rule:
        {rule}

        Input: {input_data}
        Output: {output}

        Is this output correct? Answer only TRUE or FALSE.
        """
        
        response = self.client.generate(self.model, prompt)
        clean_response = response.strip().upper()
        
        if "TRUE" in clean_response or "YES" in clean_response:
            return True
        return False
