import json
from typing import Dict, Any

def calculate_completeness(ccb: Dict[str, Any]) -> float:
    score = 0.0
    if ccb.get("alert_summary"): score += 0.2
    if ccb.get("ehr_context"): score += 0.2
    if ccb.get("patient_reported_context"): score += 0.2
    if ccb.get("clinical_considerations"): score += 0.2
    if ccb.get("recommended_actions"): score += 0.2
    return score

def check_safety_compliance(ccb: Dict[str, Any]) -> bool:
    from domain.validators import SafetyValidator
    from domain.schemas import ClinicalContextBrief
    
    try:
        model = ClinicalContextBrief(**ccb)
        validator = SafetyValidator()
        result = validator.validate(model)
        return result.passed
    except Exception:
        return False
