# engines/position_manager.py
"""Position Manager — Tracks active position state."""
class PositionManager:
    def __init__(self):
        self.active = None

    def open(self, pos: dict):
        self.active = pos

    def close(self) -> dict:
        old = self.active
        self.active = None
        return old

    def is_active(self) -> bool:
        return self.active is not None
