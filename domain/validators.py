import re
from typing import List, Optional
from pydantic import BaseModel
from domain.schemas import ClinicalContextBrief

PROHIBITED_PATTERNS = [
    r"\bdiagnosis\s+of\b",
    r"\byou\s+have\s+\b",
    r"\bthe\s+patient\s+has\s+(cancer|diabetes|hypertension)\b",
    r"\bI\s+diagnose\b",
    r"\bprescribe\b",
    r"\btake\s+\d+\s*mg\b",
    r"\blying\b",
    r"\bnot\s+taking\s+their\s+medication\b",
]

REQUIRED_ELEMENTS = [
    "disclaimer",
    "confidence_score",
    "source_citations",
]

CANONICAL_DISCLAIMER = "EDUCATIONAL PROTOTYPE ONLY"

class SafetyViolation(BaseModel):
    pattern: Optional[str] = None
    text_fragment: Optional[str] = None

class MissingRequiredField(BaseModel):
    field: str

class DisclaimerViolation(BaseModel):
    pass

class ValidationResult(BaseModel):
    passed: bool
    violations: List[BaseModel]

class SafetyValidator:
    def validate(self, ccb: ClinicalContextBrief) -> ValidationResult:
        violations = []
        
        full_text = f"{ccb.alert_summary} {ccb.ehr_context} {ccb.patient_reported_context} {' '.join(ccb.clinical_considerations)}"
        
        for pattern in PROHIBITED_PATTERNS:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                violations.append(SafetyViolation(pattern=pattern, text_fragment=match.group(0)))
                
        for field in REQUIRED_ELEMENTS:
            val = getattr(ccb, field, None)
            if val is None or (isinstance(val, str) and not val.strip()):
                violations.append(MissingRequiredField(field=field))
                
        if CANONICAL_DISCLAIMER not in ccb.disclaimer:
            violations.append(DisclaimerViolation())
            
        return ValidationResult(passed=len(violations) == 0, violations=violations)
