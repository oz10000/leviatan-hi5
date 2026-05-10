"""Cooldown Manager — Per‑asset trade spacing to prevent overtrading."""
import time


class CooldownManager:
    def __init__(self, per_asset_seconds: int = 300):
        self.per_asset_seconds = per_asset_seconds
        self._last_trade: dict = {}  # symbol → timestamp

    def can_trade(self, symbol: str) -> bool:
        if symbol not in self._last_trade:
            return True
        return (time.time() - self._last_trade[symbol]) >= self.per_asset_seconds

    def record(self, symbol: str):
        self._last_trade[symbol] = time.time()
