import pytest
from agents.triage_agent import TriageAgent
from agents.ehr_retrieval_agent import EHRRetrievalAgent
from agents.anamnesis_agent import AnamnesisAgent
from agents.synthesis_agent import SynthesisAgent

def test_agent_instantiation():
    # If .env is missing API keys, these might raise ValueError.
    try:
        triage = TriageAgent()
        assert triage.agent_name == "triage_agent"
        
        ehr = EHRRetrievalAgent()
        assert ehr.agent_name == "ehr_retrieval_agent"
        
        anamnesis = AnamnesisAgent()
        assert anamnesis.agent_name == "anamnesis_agent"
        
        synthesis = SynthesisAgent()
        assert synthesis.agent_name == "synthesis_agent"
    except ValueError as e:
        pytest.skip(f"Skipping agent test due to missing keys: {e}")
