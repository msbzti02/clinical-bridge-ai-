import uuid
from typing import Optional
from domain.schemas import ClinicalContextBrief, RPMAlert
from domain.validators import SafetyValidator
from infrastructure.logger import logger

class SafetyGuardrails:
    def __init__(self):
        self.validator = SafetyValidator()
        
    def enforce(self, ccb: ClinicalContextBrief, alert: RPMAlert) -> ClinicalContextBrief:
        result = self.validator.validate(ccb)
        
        if result.passed:
            logger.log_event("safety_guardrails_passed", alert_id=str(alert.alert_id))
            return ccb
            
        logger.log_event(
            "safety_guardrails_failed", 
            alert_id=str(alert.alert_id), 
            violations=[v.model_dump() for v in result.violations]
        )
        
        # Return a safe, degraded CCB
        safe_ccb = ClinicalContextBrief(
            alert_summary="AUTOMATED SAFETY BLOCK: Original summary contained prohibited diagnostic language or failed required elements.",
            ehr_context="[Redacted due to safety violation]",
            patient_reported_context="[Redacted due to safety violation]",
            data_conflicts=[],
            clinical_considerations=[
                "The synthesized response failed internal safety checks.",
                "Clinician must manually review the raw data for this alert."
            ],
            recommended_actions=[
                "Manual review required."
            ],
            confidence_score=0.0,
            source_citations=[],
            disclaimer="⚠️ EDUCATIONAL PROTOTYPE ONLY. This output is not a clinical tool and must not be used for actual clinical decision-making. All data is simulated. A qualified clinician must review this information before any action is taken.",
            reasoning_trace="[Redacted]"
        )
        return safe_ccb
