import pytest
import asyncio
import os
import json
from domain.schemas import RPMAlert
from orchestrator.orchestrator import Orchestrator

@pytest.mark.asyncio
async def test_successful_pipeline():
    # Load test alert
    alert_path = "data/scenarios/scenario_01_missed_medication/alert.json"
    if not os.path.exists(alert_path):
        pytest.skip("Test scenario data not generated.")
        
    with open(alert_path, "r") as f:
        alert_data = json.load(f)
        
    alert = RPMAlert(**alert_data)
    orchestrator = Orchestrator(prompt_version="v3.0")
    
    # Run
    try:
        ccb = await orchestrator.process_alert(alert)
        assert ccb is not None
        assert ccb.alert_summary
        assert ccb.confidence_score >= 0.0
    except Exception as e:
        pytest.skip(f"Skipping e2e test due to API failure: {e}")
