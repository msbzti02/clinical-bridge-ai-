import os
from typing import Dict, Any, Optional
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv

load_dotenv(override=True)

class LLMClient:
    def __init__(self):
        # Determine which model to use based on env vars
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")

    def get_model(self, model_name: str, temperature: float = 0.0, max_tokens: int = 1000):
        # Prefer Groq if key is present
        if self.groq_key:
            return ChatOpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=self.groq_key,
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
        # Fallback to OpenRouter
        if self.openrouter_key:
            return ChatOpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.openrouter_key,
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
        if "claude" in model_name.lower():
            if not self.anthropic_key or self.anthropic_key == "your_anthropic_api_key_here":
                raise ValueError("ANTHROPIC_API_KEY is missing")
            return ChatAnthropic(
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=self.anthropic_key
            )
        elif "gpt" in model_name.lower() or "o1" in model_name.lower():
            if not self.openai_key or self.openai_key == "your_openai_api_key_here":
                raise ValueError("OPENAI_API_KEY is missing")
            return ChatOpenAI(
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=self.openai_key
            )
        else:
            raise ValueError(f"Unsupported model config. Please set OPENROUTER_API_KEY.")

    async def generate_json(self, model_name: str, system_prompt: str, user_prompt: str, temperature: float = 0.0) -> str:
        model = self.get_model(model_name, temperature=temperature)
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = await model.ainvoke(messages)
        return response.content
