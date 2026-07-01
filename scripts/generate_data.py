import os
import json
import uuid
from datetime import datetime, timedelta
import random
import sys

# Add project root to path so we can import domain.schemas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from domain.schemas import (
    EHRRecord, RecordType,
    RPMAlert, DeviceType, TrendWindowItem,
    AnamnesisRecord, AnamnesisRecordType, CollectionMethod, StructuredFields, LifestyleFactors
)

def dt_str(dt: datetime) -> str:
    # Ensure standard isoformat with 'Z'
    return dt.isoformat() + "Z"

CONDITIONS = ["HTN", "DM2", "HF", "CKD", "COPD"]

def generate_patient_data(patient_index: int, condition: str, base_path: str):
    patient_id = uuid.uuid4()
    patient_dir = os.path.join(base_path, "patients", str(patient_id))
    
    ehr_dir = os.path.join(patient_dir, "ehr")
    rpm_dir = os.path.join(patient_dir, "rpm")
    anamnesis_dir = os.path.join(patient_dir, "anamnesis")
    
    os.makedirs(ehr_dir, exist_ok=True)
    os.makedirs(rpm_dir, exist_ok=True)
    os.makedirs(anamnesis_dir, exist_ok=True)
    
    # 1. EHR Records (Problem list, Meds, Visit notes)
    problem_record = EHRRecord(
        record_id=uuid.uuid4(),
        patient_id=patient_id,
        record_type=RecordType.problem_list,
        content={"condition": condition, "status": "active"},
        icd10_codes=["I10"] if condition == "HTN" else ["E11.9"] if condition == "DM2" else ["I50.9"] if condition == "HF" else ["N18.9"] if condition == "CKD" else ["J44.9"],
        timestamp=datetime.now() - timedelta(days=365),
        source_facility="Primary Care Clinic"
    )
    with open(os.path.join(ehr_dir, f"{problem_record.record_id}.json"), "w") as f:
        f.write(problem_record.model_dump_json(indent=2))

    visit_note = EHRRecord(
        record_id=uuid.uuid4(),
        patient_id=patient_id,
        record_type=RecordType.visit_note,
        content=f"Patient presents for routine follow-up of {condition}. Vitals stable. Continue current management plan.",
        timestamp=datetime.now() - timedelta(days=30),
        source_facility="Primary Care Clinic"
    )
    with open(os.path.join(ehr_dir, f"{visit_note.record_id}.json"), "w") as f:
        f.write(visit_note.model_dump_json(indent=2))

    # 2. Anamnesis Record
    anamnesis = AnamnesisRecord(
        record_id=uuid.uuid4(),
        patient_id=patient_id,
        record_type=AnamnesisRecordType.intake_form,
        content_text=f"I have been feeling okay lately, but sometimes I get a bit tired when managing my {condition}. I try to eat healthy but it's hard.",
        structured_fields=StructuredFields(
            chief_complaint="Fatigue",
            lifestyle_factors=LifestyleFactors(diet="Average", exercise="Occasional")
        ),
        collection_date=datetime.now() - timedelta(days=7),
        collection_method=CollectionMethod.simulated
    )
    with open(os.path.join(anamnesis_dir, f"{anamnesis.record_id}.json"), "w") as f:
        f.write(anamnesis.model_dump_json(indent=2))

    # 3. RPM History (just a sample, not strictly an alert, but let's make an alert history file)
    alert = RPMAlert(
        alert_id=uuid.uuid4(),
        patient_id=patient_id,
        timestamp=datetime.now() - timedelta(days=2),
        device_type=DeviceType.blood_pressure_monitor,
        measured_values={"systolic_bp": 130 + random.randint(0, 10), "diastolic_bp": 80 + random.randint(0, 10)},
        alert_category="ELEVATED",
        baseline_thresholds={"systolic_bp": {"low": 90, "high": 140}, "diastolic_bp": {"low": 60, "high": 90}}
    )
    with open(os.path.join(rpm_dir, f"{alert.alert_id}.json"), "w") as f:
        f.write(alert.model_dump_json(indent=2))
        
    return patient_id

def generate_scenarios(base_path: str, patient_ids: list):
    scenarios = [
        "scenario_01_missed_medication",
        "scenario_02_false_alarm",
        "scenario_03_silent_deterioration",
        "scenario_04_incomplete_record",
        "scenario_05_conflicting_data"
    ]
    
    for i, scenario in enumerate(scenarios):
        scenario_dir = os.path.join(base_path, "scenarios", scenario)
        os.makedirs(scenario_dir, exist_ok=True)
        
        patient_id = patient_ids[i % len(patient_ids)]
        
        alert = RPMAlert(
            alert_id=uuid.uuid4(),
            patient_id=patient_id,
            timestamp=datetime.now(),
            device_type=DeviceType.blood_pressure_monitor,
            measured_values={"systolic_bp": 178, "diastolic_bp": 105},
            alert_category="HIGH_BP_SUSTAINED",
            baseline_thresholds={"systolic_bp": {"low": 90, "high": 140}, "diastolic_bp": {"low": 60, "high": 90}}
        )
        with open(os.path.join(scenario_dir, "alert.json"), "w") as f:
            f.write(alert.model_dump_json(indent=2))
            
        gold_ccb = {
            "ccb_id": str(uuid.uuid4()),
            "patient_id": str(patient_id),
            "alert_id": str(alert.alert_id),
            "urgency_level": "Urgent",
            "alert_summary": f"Simulated gold standard for {scenario}",
            "confidence_score": 0.95,
            "disclaimer": "EDUCATIONAL PROTOTYPE ONLY.",
            "source_citations": []
        }
        with open(os.path.join(scenario_dir, "gold_standard_ccb.json"), "w") as f:
            json.dump(gold_ccb, f, indent=2)

def main():
    base_path = os.path.join(os.path.dirname(__file__), "..", "data")
    
    print("Generating 15 patients...")
    patient_ids = []
    for i in range(15):
        condition = CONDITIONS[i % len(CONDITIONS)]
        pid = generate_patient_data(i, condition, base_path)
        patient_ids.append(pid)
        
    print("Generating 5 scenarios...")
    generate_scenarios(base_path, patient_ids)
    print("Done!")

if __name__ == "__main__":
    main()
