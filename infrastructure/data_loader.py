import os
import json
from uuid import UUID
from typing import List, Optional
from domain.schemas import EHRRecord, RPMAlert, AnamnesisRecord

class DataLoader:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.patients_dir = os.path.join(self.data_dir, "patients")
        
    def _load_json_files(self, directory: str) -> List[dict]:
        data = []
        if not os.path.exists(directory):
            return data
        for filename in os.listdir(directory):
            if filename.endswith(".json"):
                with open(os.path.join(directory, filename), "r") as f:
                    data.append(json.load(f))
        return data

    def get_ehr_records(self, patient_id: UUID) -> List[EHRRecord]:
        ehr_dir = os.path.join(self.patients_dir, str(patient_id), "ehr")
        records = self._load_json_files(ehr_dir)
        return [EHRRecord(**r) for r in records]

    def get_rpm_alerts(self, patient_id: UUID) -> List[RPMAlert]:
        rpm_dir = os.path.join(self.patients_dir, str(patient_id), "rpm")
        records = self._load_json_files(rpm_dir)
        return [RPMAlert(**r) for r in records]

    def get_anamnesis_records(self, patient_id: UUID) -> List[AnamnesisRecord]:
        anamnesis_dir = os.path.join(self.patients_dir, str(patient_id), "anamnesis")
        records = self._load_json_files(anamnesis_dir)
        return [AnamnesisRecord(**r) for r in records]
