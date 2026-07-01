import pytest
from datetime import datetime
from uuid import uuid4
from domain.schemas import (
    EHRRecord, RecordType,
    RPMAlert, DeviceType, TrendWindowItem,
    AnamnesisRecord, AnamnesisRecordType, CollectionMethod, StructuredFields
)

def test_ehr_record_creation():
    record = EHRRecord(
        record_id=uuid4(),
        patient_id=uuid4(),
        record_type=RecordType.visit_note,
        content="Patient presents with hypertension.",
        timestamp=datetime.now(),
        source_facility="General Hospital"
    )
    assert record.record_type == RecordType.visit_note

def test_rpm_alert_creation():
    alert = RPMAlert(
        alert_id=uuid4(),
        patient_id=uuid4(),
        timestamp=datetime.now(),
        device_type=DeviceType.blood_pressure_monitor,
        measured_values={"systolic_bp": 150, "diastolic_bp": 95},
        alert_category="HIGH_BP",
        baseline_thresholds={"systolic_bp": {"low": 90, "high": 140}}
    )
    assert alert.device_type == DeviceType.blood_pressure_monitor
    assert alert.measured_values["systolic_bp"] == 150

def test_anamnesis_record_creation():
    record = AnamnesisRecord(
        record_id=uuid4(),
        patient_id=uuid4(),
        record_type=AnamnesisRecordType.intake_form,
        content_text="This is a sufficiently long narrative text about the patient's symptoms and history that meets the 50 character limit requirement.",
        collection_date=datetime.now(),
        collection_method=CollectionMethod.simulated,
        structured_fields=StructuredFields(chief_complaint="Headache")
    )
    assert record.record_type == AnamnesisRecordType.intake_form
    assert record.structured_fields.chief_complaint == "Headache"
