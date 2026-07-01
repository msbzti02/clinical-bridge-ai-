import os
import yaml
from typing import Dict, Any

class PromptRegistry:
    def __init__(self, prompts_dir: str = "prompts"):
        self.prompts_dir = prompts_dir

    def load_prompt(self, agent_name: str, version: str) -> Dict[str, Any]:
        prompt_path = os.path.join(self.prompts_dir, agent_name, f"{version}.yaml")
        if not os.path.exists(prompt_path):
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
            
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_data = yaml.safe_load(f)
            
        self._validate_prompt(prompt_data, agent_name, version)
        return prompt_data
        
    def _validate_prompt(self, data: Dict[str, Any], agent_name: str, version: str):
        required_fields = ["version", "agent", "model", "temperature", "system_prompt"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Prompt {agent_name}/{version} missing required field: {field}")
                
        v = str(version)
        if v.startswith("v"):
            v = v[1:]
        if str(data["version"]) != v:
            raise ValueError(f"Version mismatch in {agent_name}/{version}.yaml")
