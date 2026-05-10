"""
State Manager — Crash‑proof persistence.

Uses atomic write (write to .tmp → rename) to prevent corruption.
Stores: equity, peak, mode, last trade times.
"""
import json
import os
import tempfile
import config
from services.logger import get_logger

logger = get_logger(__name__)


class StateManager:
    def __init__(self, filepath: str = None):
        self.filepath = filepath or config.STATE_FILE
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        self._state: dict = {
            "equity": config.INITIAL_CAPITAL,
            "peak": config.INITIAL_CAPITAL,
            "mode": config.MODE,
            "total_trades": 0,
            "cooldowns": {},
        }
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    loaded = json.load(f)
                self._state.update(loaded)
                logger.info(f"State loaded: equity={self._state['equity']:.2f}, "
                            f"peak={self._state['peak']:.2f}")
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"State file corrupted ({e}), using defaults")

    def save(self, **kwargs):
        """Atomic save: write temp, then rename."""
        self._state.update(kwargs)
        tmp_path = self.filepath + ".tmp"
        try:
            with open(tmp_path, "w") as f:
                json.dump(self._state, f, indent=2)
            os.replace(tmp_path, self.filepath)
        except Exception as e:
            logger.error(f"State save failed: {e}")

    def get(self, key: str, default=None):
        return self._state.get(key, default)

    def increment_trades(self):
        self._state["total_trades"] = self._state.get("total_trades", 0) + 1
        self.save()
