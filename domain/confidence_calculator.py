from typing import Optional
from domain.schemas import EHRFindings, AnamnesisFindings

class ConfidenceCalculator:
    def calculate(self, ehr_findings: Optional[EHRFindings], anamnesis_findings: Optional[AnamnesisFindings]) -> float:
        score = 0.5  # Base score
        
        if ehr_findings and ehr_findings.retrieved_chunks:
            score += 0.2
            if len(ehr_findings.retrieved_chunks) >= 3:
                score += 0.1
                
        if anamnesis_findings and anamnesis_findings.extracted_complaints:
            score += 0.2
            
        if anamnesis_findings and anamnesis_findings.discrepancy_flags:
            score -= 0.1
            
        return round(max(0.0, min(1.0, score)), 2)
