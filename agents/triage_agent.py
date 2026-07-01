from domain.schemas import RPMAlert, TriageDecision
from agents.base_agent import BaseAgent

class TriageAgent(BaseAgent):
    def __init__(self, version: str = "v1.0"):
        super().__init__("triage_agent", version)
        
    async def triage(self, alert: RPMAlert) -> TriageDecision:
        user_prompt = f"RPM Alert:\n{alert.model_dump_json(indent=2)}"
        
        try:
            decision = await self.run_structured(user_prompt, TriageDecision)
            return decision
        except Exception as e:
            raise RuntimeError(f"Failed to execute TriageAgent: {str(e)}")
