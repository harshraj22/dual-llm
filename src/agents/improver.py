from .llm import OllamaClient
from src.utils.logger import setup_logger

logger = setup_logger("ImproverAgent")

class ImproverAgent:
    def __init__(self, model_name: str, base_url: str):
        self.model = model_name
        self.client = OllamaClient(base_url=base_url)

    def improve(self, current_script, failures):
        logger.info(f"Improving script based on {len(failures)} failures.")
        
        failure_text = "\n".join([f"- Input: {f[0]}, Output: {f[1]}" for f in failures])
        
        prompt = f"""
        Your task is to fix a python script that solves the Prime Number problem.
        The function must be named `solve(n)` and take one integer argument.
        It should return True if n is prime, and False otherwise.

        Current Script:
        ```python
        {current_script}
        ```

        The script FAILED on the following inputs:
        {failure_text}

        Please rewrite the ENTIRE script to fix these errors. ensure the function is named `solve`.
        Do not explain. Return only the python code.
        """
        
        response = self.client.generate(self.model, prompt)
        
        # Simple cleanup to extract code block if wrapped in markdown
        if "```python" in response:
            response = response.split("```python")[1].split("```")[0]
        elif "```" in response:
            response = response.split("```")[1].split("```")[0]
            
        return response.strip()
