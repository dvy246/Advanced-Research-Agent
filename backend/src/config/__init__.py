import yaml
from pathlib import Path

def yaml_load(prompt_key: str):
    """
    Loads a prompt configuration from the 'prompts.yaml' file.

    Args:
        prompt_key (str): The key corresponding to the desired prompt.

    Returns:
        str or dict: The loaded prompt associated with the specified key.

    Raises:
        FileNotFoundError: If the 'prompts.yaml' file does not exist.
        KeyError: If the provided key is not found in the YAML file.
        yaml.YAMLError: If the YAML file cannot be parsed.
    """
    yaml_path = Path(__file__).parent.resolve() / "prompts.yaml"

    if not yaml_path.exists():
        raise FileNotFoundError(f"Configuration file '{yaml_path}' not found.")

    with open(yaml_path, "r") as file:
        try:
            prompt_data = yaml.safe_load(file)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error parsing YAML file: {e}")

        if prompt_key not in prompt_data:
            raise KeyError(f"Prompt key '{prompt_key}' not found in '{yaml_path}'.")

        return prompt_data[prompt_key]