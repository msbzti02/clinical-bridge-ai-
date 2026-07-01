import json
import os
from datetime import datetime
import logging
from typing import Any, Dict

# Set up basic logging for console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class JSONLLogger:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        # One log file per run/day
        date_str = datetime.now().strftime("%Y-%m-%d")
        self.log_file = os.path.join(self.log_dir, f"run_{date_str}.jsonl")
        
    def log_event(self, event_type: str, **kwargs: Any) -> None:
        log_entry = {
            "event_type": event_type,
            "timestamp": datetime.now().isoformat() + "Z",
        }
        log_entry.update(kwargs)
        
        # Log to file
        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
            
        # Log to console
        logging.info(f"[{event_type}] {json.dumps(kwargs)}")

logger = JSONLLogger()
