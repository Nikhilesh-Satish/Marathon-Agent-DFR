

import json

class BuildScheduler:
    def __init__(self, architecture_contract_path: str):
        with open(architecture_contract_path, "r") as f:
            self.contract = json.load(f)

        self.build_order = self.contract["build_order"]
        self.batches = self.contract["batches"]

    def get_ordered_stages(self):
        """
        Returns ordered list of build stages with their files.
        Example:
        [
            {"stage": "backend", "files": ["api.py", "db.py"]},
            {"stage": "frontend", "files": ["app.tsx"]},
            {"stage": "config", "files": ["env.yaml"]}
        ]
        """
        stages = []
        for stage in self.build_order:
            if stage not in self.batches:
                raise ValueError(f"Stage '{stage}' missing from batches in Architecture Contract")

            stages.append({
                "stage": stage,
                "files": self.batches[stage]
            })

        return stages
