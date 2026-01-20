
import time
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_requests_per_minute=10, max_tokens_per_minute=20000):
        self.max_rpm = max_requests_per_minute
        self.max_tpm = max_tokens_per_minute

        self.request_times = []
        self.token_usage = []

    def _cleanup_old(self):
        one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
        self.request_times = [t for t in self.request_times if t > one_minute_ago]
        self.token_usage = [t for t in self.token_usage if t["time"] > one_minute_ago]

    def check_and_wait(self, estimated_tokens, ledger):
        """
        Blocks execution until rate limits are safe.
        Writes pause/resume info to ledger if sleep is required.
        """
        while True:
            self._cleanup_old()

            current_rpm = len(self.request_times)
            current_tpm = sum(t["tokens"] for t in self.token_usage)

            if current_rpm < self.max_rpm and current_tpm + estimated_tokens < self.max_tpm:
                # Safe to proceed
                self.request_times.append(datetime.utcnow())
                self.token_usage.append({
                    "time": datetime.utcnow(),
                    "tokens": estimated_tokens
                })
                return
            else:
                # Need to sleep
                ledger.log_event({
                    "type": "RATE_LIMIT_SLEEP",
                    "timestamp": datetime.utcnow().isoformat(),
                    "reason": "RPM/TPM exceeded"
                })
                time.sleep(5)  # sleep in small chunks, re-check deterministically
