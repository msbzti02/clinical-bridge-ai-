import os
import argparse
from uuid import UUID
from infrastructure.data_loader import DataLoader
from infrastructure.vector_store import VectorStore

def init_vector_store():
    print("Initializing Vector Store with simulated data...")
    loader = DataLoader()
    vstore = VectorStore()
    
    patients_dir = loader.patients_dir
    if not os.path.exists(patients_dir):
        print("No patient data found. Please run generate_data.py first.")
        return
        
    for pid_str in os.listdir(patients_dir):
        try:
            pid = UUID(pid_str)
            ehr_records = loader.get_ehr_records(pid)
            if ehr_records:
                print(f"Indexing {len(ehr_records)} EHR records for patient {pid_str}")
                vstore.add_ehr_records(ehr_records)
        except ValueError:
            continue
            
    print("Vector Store initialization complete.")

def health_check():
    print("Running Health Check...")
    loader = DataLoader()
    vstore = VectorStore()
    print("Vector Store connected successfully.")
    
    patient_count = 0
    if os.path.exists(loader.patients_dir):
        patient_count = len(os.listdir(loader.patients_dir))
    print(f"Found {patient_count} patients.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--init-vector-store", action="store_true")
    parser.add_argument("--health-check", action="store_true")
    args = parser.parse_args()
    
    if args.init_vector_store:
        init_vector_store()
    if args.health_check:
        health_check()
    if not any(vars(args).values()):
        parser.print_help()
