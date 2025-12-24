import sys
import os

# Ensure src is in python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.dataset.primes.dataset import PrimeDataset
from src.agents.evaluator import EvaluatorAgent
from src.agents.improver import ImproverAgent
from src.utils.runner import run_script
from src.utils.config_loader import load_config
from src.utils.logger import setup_logger, update_log_levels, setup_raw_logger
import os
import litellm
from prometheus_client import start_http_server

logger = setup_logger("Main")
table_logger = setup_raw_logger("Table")

def main():
    # Enable LiteLLM Prometheus Metrics (Optional, as we have custom metrics now)
    litellm.callbacks = ["prometheus"]

    # Start Prometheus metrics server
    try:
        start_http_server(8000)
        logger.info("Prometheus metrics server started on port 8000")
    except Exception as e:
        logger.warning(f"Failed to start metrics server: {e}")

    try:
        config = load_config()
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return

    # Logging Configuration Precedence: Env > Config > Default
    env_level = os.getenv("LOG_LEVEL")
    if env_level:
        logger.info(f"Log level set from Environment Variable: {env_level}")
        # update_log_levels is not strictly needed if env var was present during init, 
        # but good for consistency or if we want to support runtime changes later.
        # However, setup_logger reads ENV var already. 
        # The key case is when ENV is NOT set, we want to apply Config value.
        pass
    else:
        config_level = config.get('logging', {}).get('level', 'INFO')
        logger.info(f"Log level set from Config File: {config_level}")
        update_log_levels(config_level)

    logger.info("Welcome to the Dual LLM Self-Correction Loop")
    logger.info(f"Using models - Evaluator: {config['llm']['evaluator_model']}, Improver: {config['llm']['improver_model']}")
    
    # 1. Setup
    dataset = PrimeDataset(
        range_start=config['dataset']['range_start'], 
        range_end=config['dataset']['range_end']
    )
    
    base_url = config['ollama_base_url']
    evaluator = EvaluatorAgent(model_name=config['llm']['evaluator_model'], base_url=base_url)
    improver = ImproverAgent(model_name=config['llm']['improver_model'], base_url=base_url)
    
    # Initial Script (Intentionally Flawed or Empty)
    current_script = """
def solve(n):
    # I don't know what to do yet
    return False
"""
    
    max_iterations = config['loop']['max_iterations']
    show_all = config['logging']['show_all_data_points']
    max_failures = config['logging']['max_failures_to_log']

    for i in range(max_iterations):
        logger.info(f"--- Iteration {i+1}/{max_iterations} ---")
        logger.info("Current Script:\n" + current_script.strip())
        
        failures = []
        data_points = dataset.get_data()
        correct_count = 0
        total_checks = len(data_points)
        
        # 2. Run & Evaluate
        logger.info("Running script on dataset...")
        
        # Header for Table - Using table_logger for clean output
        if show_all:
             table_logger.info(f"{'Data ID':<36} | {'Script Output':<15} | {'Expected':<10} | {'Agent Check':<15}")
             table_logger.info("-" * 83)

        for data in data_points:
            # Run Script on CONTENT, not the full object
            output = run_script(current_script, data.content)
            
            # Ground Truth Check - validate handles/expects DataPoint (we updated it) or content
            is_correct_ground_truth = dataset.validate(data, output)

            # Get Expected Value for logging
            # Since we know this is PrimeDataset, we can calculate it
            expected_val = dataset._is_prime(data.content)
            
            # Ask Evaluator Agent - Pass Content for context
            rule = dataset.get_instruction()
            is_correct_agent = evaluator.evaluate(data.content, output, rule)
            
            # Log ID instead of content
            status_line = f"{str(data.id):<36} | {str(output):<15} | {str(expected_val):<10} | {str(is_correct_agent):<15}"
            
            # Logging Logic
            if not is_correct_agent:
                # Store (Input Content, Output) tuple for Improver, because Improver needs context
                # Or pass full DataPoint? Improver prompt expects "Input: X, Output: Y".
                # Let's pass (data.content, output) to failures list for Improver clarity
                failures.append((data.content, output))
                
                if not show_all and len(failures) <= max_failures:
                    if len(failures) == 1:
                         # Print header on first failure if not showing all
                         print(f"{'Data ID':<36} | {'Script Output':<15} | {'Expected':<10} | {'Agent Check':<15}")
                         print("-" * 83)
                    print(status_line)
            else:
                correct_count += 1
                if show_all:
                    print(status_line)
        
        if not show_all and len(failures) > max_failures:
             print(f"... and {len(failures) - max_failures} more failures.")

        # 3. Check Termination
        logger.info(f"Score: {correct_count}/{total_checks}")
        
        if len(failures) == 0:
            logger.info("SUCCESS! The script has passed all evaluations.")
            
            output_dir = "outputs"
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, "final_script.py")
            
            with open(output_path, "w") as f:
                f.write(current_script)
            logger.info(f"Saved to {output_path}")
            break
            
        if i == max_iterations - 1:
            logger.info("Max iterations reached without full success.")
            break
            
        # 4. Improve
        logger.info(f"Found {len(failures)} failures. Asking Improver to fix...")
        current_script = improver.improve(current_script, failures)
        
if __name__ == "__main__":
    main()
