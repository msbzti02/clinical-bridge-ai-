from pydantic import BaseModel, Field, constr
from typing import List, Dict, Optional, Union, Any
from datetime import datetime
from enum import Enum
from uuid import UUID

class RecordType(str, Enum):
    problem_list = "problem_list"
    medication = "medication"
    lab_result = "lab_result"
    visit_note = "visit_note"
    allergy = "allergy"

class EHRRecord(BaseModel):
    record_id: UUID = Field(description="Unique identifier for this EHR record")
    patient_id: UUID = Field(description="FK to patient")
    record_type: RecordType
    content: Union[str, dict] = Field(description="Free text for visit_note; structured dict for others")
    icd10_codes: Optional[List[str]] = Field(default=None, description="Valid ICD-10 codes; only for problem_list records")
    timestamp: datetime
    source_facility: Optional[str] = None

class DeviceType(str, Enum):
    blood_pressure_monitor = "blood_pressure_monitor"
    glucometer = "glucometer"
    weight_scale = "weight_scale"
    pulse_oximeter = "pulse_oximeter"
    ecg_patch = "ecg_patch"
    activity_tracker = "activity_tracker"

class TrendWindowItem(BaseModel):
    timestamp: datetime
    values: Dict[str, float]

class RPMAlert(BaseModel):
    alert_id: UUID
    patient_id: UUID
    timestamp: datetime
    device_type: DeviceType
    device_id: Optional[str] = None
    measured_values: Dict[str, float] = Field(description="Key-value pairs of measurement name to numeric value")
    alert_category: str
    baseline_thresholds: Dict[str, Dict[str, float]] = Field(description="Per-metric threshold ranges: {metric: {low: float, high: float}}")
    raw_trend_window: Optional[List[TrendWindowItem]] = Field(default=None, description="Last 7-14 readings for trend analysis")

class AnamnesisRecordType(str, Enum):
    intake_form = "intake_form"
    symptom_diary = "symptom_diary"
    medication_adherence_log = "medication_adherence_log"

class LifestyleFactors(BaseModel):
    diet: Optional[str] = None
    exercise: Optional[str] = None
    alcohol: Optional[str] = None
    smoking: Optional[str] = None

class StructuredFields(BaseModel):
    chief_complaint: Optional[str] = None
    symptom_onset: Optional[str] = None
    medications_reported: Optional[List[str]] = None
    adherence_self_reported: Optional[Dict[str, bool]] = None
    lifestyle_factors: Optional[LifestyleFactors] = None

class CollectionMethod(str, Enum):
    intake_form = "intake_form"
    phone_interview = "phone_interview"
    patient_portal = "patient_portal"
    simulated = "simulated"

class AnamnesisRecord(BaseModel):
    record_id: UUID
    patient_id: UUID
    record_type: AnamnesisRecordType
    content_text: str = Field(min_length=50, description="Patient-voice narrative text; minimum 50 characters")
    structured_fields: Optional[StructuredFields] = None
    collection_date: datetime
    collection_method: Optional[CollectionMethod] = None

class TriageDecision(BaseModel):
    urgency_level: str
    urgency_rationale: str
    clinical_question: str
    ehr_query_params: Dict[str, Any]
    anamnesis_query_params: Dict[str, Any]
    reasoning_trace: str
    escalate_immediately: bool

class EHRChunk(BaseModel):
    chunk_id: str
    document: str
    metadata: Dict[str, Any]
    distance: float

class EHRFindings(BaseModel):
    retrieved_chunks: List[EHRChunk]
    summary: str
    key_findings: List[str]
    citations: List[str]

class AnamnesisFindings(BaseModel):
    extracted_complaints: List[str]
    discrepancy_flags: List[str]

class ClinicalContextBrief(BaseModel):
    alert_summary: str
    ehr_context: str
    patient_reported_context: str
    data_conflicts: List[str]
    clinical_considerations: List[str]
    recommended_actions: List[str]
    confidence_score: float
    source_citations: List[str]
    disclaimer: str
    reasoning_trace: str
