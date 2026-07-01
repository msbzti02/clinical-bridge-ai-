from typing import Type, TypeVar, Optional, Any
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
import asyncio
from infrastructure.prompt_registry import PromptRegistry
from infrastructure.llm_client import LLMClient
from infrastructure.logger import logger

T = TypeVar('T', bound=BaseModel)

class BaseAgent:
    def __init__(self, agent_name: str, version: str = "v1.0"):
        self.agent_name = agent_name
        self.version = version
        self.prompt_registry = PromptRegistry()
        self.llm_client = LLMClient()
        self.config = self.prompt_registry.load_prompt(agent_name, version)
        
    async def run_structured(self, user_prompt: str, output_schema_class: Type[BaseModel]) -> BaseModel:
        # Load prompt version
        try:
            config = self.config
            system_prompt_str = config.get("system_prompt", "")
            if "safety_constraints" in config:
                system_prompt_str += "\n\nSAFETY CONSTRAINTS:\n" + "\n".join(f"- {c}" for c in config["safety_constraints"])
            
            model_name = config.get("model", "llama-3.1-8b-instant")
            temperature = config.get("temperature", 0.0)
            
            from langchain_core.messages import SystemMessage
            
            # Build LangChain prompt template
            prompt_template = ChatPromptTemplate.from_messages([
                SystemMessage(content=system_prompt_str),
                ("human", "{user_prompt}")
            ])
            
            # Retry loop for flaky models
            max_retries = 3
            current_temp = temperature
            
            for attempt in range(max_retries):
                try:
                    # Get the underlying LangChain model with current temperature
                    model = self.llm_client.get_model(model_name, temperature=current_temp)
                    
                    # Ensure we use structured output parsing
                    chain = prompt_template | model.with_structured_output(output_schema_class)
                    
                    logger.log_event(
                        event_type="agent_run_start",
                        agent=self.agent_name,
                        version=self.version,
                        model=model_name,
                        temperature=current_temp
                    )
                    
                    response = await chain.ainvoke({"user_prompt": user_prompt})
                    
                    logger.log_event(
                        event_type="agent_run_success",
                        agent=self.agent_name
                    )
                    return response
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    logger.log_event("agent_retry", agent=self.agent_name, attempt=attempt+1, error=str(e), temperature=current_temp)
                    current_temp += 0.3  # Bump temperature to break deterministic hallucination loops
                    await asyncio.sleep(1)
            
        except Exception as e:
            logger.log_event(
                event_type="agent_run_error",
                agent=self.agent_name,
                error=str(e)
            )
            raise e
