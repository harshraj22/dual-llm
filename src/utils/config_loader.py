import yaml
import os

def load_config(config_path="config.yaml"):
    """
    Loads configuration from a YAML file.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found at {config_path}")
        
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        
    # Optional: Override with Env Vars
    if "OLLAMA_BASE_URL" in os.environ:
        config["ollama_base_url"] = os.environ["OLLAMA_BASE_URL"]
        
    return config
