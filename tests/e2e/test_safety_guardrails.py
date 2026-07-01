import pytest
from domain.schemas import ClinicalContextBrief, RPMAlert
from orchestrator.safety_guardrails import SafetyGuardrails
from datetime import datetime
import uuid

def test_guardrails_blocks_diagnosis():
    ccb = ClinicalContextBrief(
        alert_summary="The patient has diabetes.",
        ehr_context="",
        patient_reported_context="",
        data_conflicts=[],
        clinical_considerations=[],
        recommended_actions=[],
        confidence_score=0.9,
        source_citations=[],
        disclaimer="EDUCATIONAL PROTOTYPE ONLY.",
        reasoning_trace=""
    )
    alert = RPMAlert(
        alert_id=uuid.uuid4(),
        patient_id=uuid.uuid4(),
        timestamp=datetime.now(),
        device_type="blood_pressure_monitor",
        measured_values={"systolic": 120},
        alert_category="routine",
        baseline_thresholds={}
    )
    
    guardrails = SafetyGuardrails()
    safe_ccb = guardrails.enforce(ccb, alert)
    
    assert safe_ccb.confidence_score == 0.0
    assert "AUTOMATED SAFETY BLOCK" in safe_ccb.alert_summary
