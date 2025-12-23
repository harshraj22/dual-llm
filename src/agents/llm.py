import sys
import os
import time
from typing import List, Dict, Any, Optional
from litellm import completion
from src.utils.logger import setup_logger

logger = setup_logger("OllamaClient")

from prometheus_client import Counter, Histogram

# Custom Application Metrics
LLM_REQUESTS = Counter('dual_llm_requests_total', 'Total number of LLM requests', ['model', 'status'])
LLM_FAILURES = Counter('dual_llm_failures_total', 'Total number of failed LLM requests', ['model'])
LLM_LATENCY = Histogram('dual_llm_request_duration_seconds', 'LLM Request Duration in seconds', ['model'])

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        # LiteLLM handles the base_url configuration via environment variables or defaults
        # For Ollama, we typically just need the model name prefixed with 'ollama/'
        self.base_url = base_url

    def generate(self, model: str, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generates text using the specified model via LiteLLM.
        """
        # Ensure model name is correctly formatted for LiteLLM if using Ollama
        if not model.startswith("ollama/"):
             # Simple heuristic: if it looks like an ollama model, prefix it
             litellm_model = f"ollama/{model}"
        else:
             litellm_model = model

        messages = []
        if system_prompt:
             messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})

        # Log the request at DEBUG level
        logger.debug(f"Requesting model: {litellm_model}")
        logger.debug(f"System Prompt: {system_prompt}")
        logger.debug(f"User Prompt: {prompt}")

        start_time = time.time()
        try:
            response = completion(
                model=litellm_model, 
                messages=messages, 
                api_base=self.base_url
            )
            duration = time.time() - start_time
            
            # Log full response metadata at DEBUG level
            logger.debug(f"Full Response Object: {response}")

            # Attempt to extract reasoning if available (common in reasoning models)
            if hasattr(response.choices[0], 'message') and hasattr(response.choices[0].message, 'reasoning_content'):
                reasoning = response.choices[0].message.reasoning_content
                if reasoning:
                    logger.debug(f"LLM Reasoning: {reasoning}")
            
            # Record Success and Latency
            LLM_REQUESTS.labels(model=model, status="success").inc()
            LLM_LATENCY.labels(model=model).observe(duration)
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error communicating with LiteLLM: {e}")
            # Record Failure
            LLM_REQUESTS.labels(model=model, status="failure").inc()
            LLM_FAILURES.labels(model=model).inc()
            return ""

if __name__ == "__main__":
    # Test
    client = OllamaClient()
    print(client.generate("gemma3:4b", "Say hello"))

