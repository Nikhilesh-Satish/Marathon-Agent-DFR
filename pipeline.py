
import json
import os
from scheduler import BuildScheduler
from rate_limiter import RateLimiter
from ledger import Ledger
from gemini_batch import GeminiBatchGenerator

class BuildPipeline:
    def __init__(self, architecture_contract_path, output_dir="generated", ledger_path="ledger.json"):
        self.arch_path = architecture_contract_path
        self.output_dir = output_dir

        with open(self.arch_path, "r") as f:
            self.arch_text = f.read()

        self.scheduler = BuildScheduler(self.arch_path)
        self.rate_limiter = RateLimiter()
        self.ledger = Ledger(ledger_path)
        self.generator = GeminiBatchGenerator()

    def run(self):
        stages = self.scheduler.get_ordered_stages()
        last_completed = self.ledger.get_last_completed_stage()

        skip = True if last_completed else False

        for stage_info in stages:
            stage = stage_info["stage"]
            files = stage_info["files"]

            if skip:
                if stage == last_completed:
                    skip = False
                continue

            print(f"\n[BUILD] Starting stage: {stage}")

            estimated_tokens = 2000 * len(files)
            self.rate_limiter.check_and_wait(estimated_tokens, self.ledger)

            try:
                generated, checksums = self.generator.generate_stage(
                    stage=stage,
                    files=files,
                    architecture_text=self.arch_text,
                    output_dir=self.output_dir
                )

                self.ledger.log_stage_complete(stage, list(generated.keys()), checksums)

                print(f"[BUILD] Completed stage: {stage}")

            except Exception as e:
                self.ledger.log_pause(str(e), stage)
                raise RuntimeError(f"Build paused at stage {stage}: {e}")
