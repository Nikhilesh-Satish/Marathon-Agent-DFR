
import json
import os
from datetime import datetime
import hashlib

class Ledger:
    def __init__(self, ledger_path="ledger.json"):
        self.ledger_path = ledger_path

        if not os.path.exists(self.ledger_path):
            with open(self.ledger_path, "w") as f:
                json.dump([], f)

    def _read(self):
        with open(self.ledger_path, "r") as f:
            return json.load(f)

    def _write(self, entries):
        with open(self.ledger_path, "w") as f:
            json.dump(entries, f, indent=2)

    def log_event(self, event):
        entries = self._read()
        event["timestamp"] = datetime.utcnow().isoformat()

        # Hash chaining (simple but effective)
        previous_hash = entries[-1]["hash"] if entries else "GENESIS"
        event_str = json.dumps(event, sort_keys=True)
        current_hash = hashlib.sha256((previous_hash + event_str).encode()).hexdigest()

        event["prev_hash"] = previous_hash
        event["hash"] = current_hash

        entries.append(event)
        self._write(entries)

    def log_stage_complete(self, stage, files, checksums):
        self.log_event({
            "type": "STAGE_COMPLETE",
            "stage": stage,
            "files": files,
            "checksums": checksums
        })

    def log_pause(self, reason, stage):
        self.log_event({
            "type": "PAUSE",
            "reason": reason,
            "stage": stage
        })

    def get_last_completed_stage(self):
        entries = self._read()
        completed = [e for e in entries if e.get("type") == "STAGE_COMPLETE"]
        if not completed:
            return None
        return completed[-1]["stage"]
