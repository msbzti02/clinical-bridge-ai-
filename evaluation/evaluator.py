import os
import json
import argparse
import asyncio
import time
from domain.schemas import RPMAlert
from orchestrator.orchestrator import Orchestrator
from evaluation.metrics import calculate_completeness, check_safety_compliance

async def run_scenario(scenario_dir: str) -> dict:
    with open(os.path.join(scenario_dir, "alert.json"), "r") as f:
        alert_data = json.load(f)
        
    alert = RPMAlert(**alert_data)
    orchestrator = Orchestrator(prompt_version="v3.0")
    
    try:
        start_time = time.time()
        ccb = await orchestrator.process_alert(alert)
        end_time = time.time()
        
        ccb_dict = ccb.model_dump()
        
        return {
            "success": True,
            "ccb": ccb_dict,
            "metrics": {
                "completeness_score": calculate_completeness(ccb_dict),
                "safety_compliance": check_safety_compliance(ccb_dict),
                "time_to_brief_seconds": round(end_time - start_time, 2)
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def evaluate_all():
    scenarios_dir = "data/scenarios"
    if not os.path.exists(scenarios_dir):
        print("Scenarios not found.")
        return
        
    results = {}
    for scenario in os.listdir(scenarios_dir):
        print(f"Evaluating {scenario}...")
        path = os.path.join(scenarios_dir, scenario)
        if os.path.isdir(path):
            result = asyncio.run(run_scenario(path))
            results[scenario] = result
            
    os.makedirs("evaluation/results", exist_ok=True)
    with open("evaluation/results/evaluation_report.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Evaluation complete. Report saved.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", action="store_true")
    args = parser.parse_args()
    
    if args.report:
        evaluate_all()
    else:
        evaluate_all()
