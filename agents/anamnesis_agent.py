import json
from uuid import UUID
from typing import Dict, Any
from domain.schemas import AnamnesisFindings
from agents.base_agent import BaseAgent
from infrastructure.data_loader import DataLoader

class AnamnesisAgent(BaseAgent):
    def __init__(self, version: str = "v1.0"):
        super().__init__("anamnesis_agent", version)
        self.data_loader = DataLoader()
        
    async def retrieve(self, patient_id: str, query_params: Dict[str, Any], clinical_question: str) -> AnamnesisFindings:
        records = self.data_loader.get_anamnesis_records(UUID(patient_id))
        
        records_json = json.dumps([r.model_dump() for r in records], indent=2, default=str)
        user_prompt = f"Clinical Question: {clinical_question}\nAnamnesis Records:\n{records_json}"
        
        try:
            findings = await self.run_structured(user_prompt, AnamnesisFindings)
            return findings
        except Exception as e:
            raise RuntimeError(f"Failed to execute AnamnesisAgent: {str(e)}")
