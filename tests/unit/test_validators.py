import pytest
from domain.schemas import ClinicalContextBrief
from domain.validators import SafetyValidator

def test_safety_validator_passes():
    ccb = ClinicalContextBrief(
        alert_summary="Patient reports fatigue.",
        ehr_context="History of HTN.",
        patient_reported_context="Feels tired.",
        data_conflicts=[],
        clinical_considerations=["Monitor BP"],
        recommended_actions=["Follow up"],
        confidence_score=0.8,
        source_citations=["doc1"],
        disclaimer="⚠️ EDUCATIONAL PROTOTYPE ONLY. This output is not a clinical tool.",
        reasoning_trace="Reasoning..."
    )
    validator = SafetyValidator()
    result = validator.validate(ccb)
    assert result.passed

def test_safety_validator_fails_prohibited():
    ccb = ClinicalContextBrief(
        alert_summary="I diagnose you with hypertension.",
        ehr_context="",
        patient_reported_context="",
        data_conflicts=[],
        clinical_considerations=[],
        recommended_actions=[],
        confidence_score=0.8,
        source_citations=["doc1"],
        disclaimer="⚠️ EDUCATIONAL PROTOTYPE ONLY. This output is not a clinical tool.",
        reasoning_trace="Reasoning..."
    )
    validator = SafetyValidator()
    result = validator.validate(ccb)
    assert not result.passed
    assert len(result.violations) > 0
