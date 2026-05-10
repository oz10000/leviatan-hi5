"""
Loop Guardian — Prevents duplicate bot instances via lock file.

Uses PID‑based locking with staleness detection.
"""
import os
import sys


LOCK_FILE = "/tmp/leviathan_highfive_v5.lock"


class LoopGuardian:
    def __init__(self, lock_path: str = LOCK_FILE):
        self.lock_path = lock_path

    def acquire(self):
        if os.path.exists(self.lock_path):
            try:
                with open(self.lock_path, "r") as f:
                    old_pid = int(f.read().strip())
                # Check if process still exists
                os.kill(old_pid, 0)
                print(f"[GUARDIAN] Another instance running (PID {old_pid}). "
                      f"Remove {self.lock_path} if stale.")
                sys.exit(1)
            except (OSError, ValueError):
                # Stale lock or invalid PID — remove it
                os.remove(self.lock_path)

        with open(self.lock_path, "w") as f:
            f.write(str(os.getpid()))

    def release(self):
        if os.path.exists(self.lock_path):
            try:
                os.remove(self.lock_path)
            except OSError:
                pass
