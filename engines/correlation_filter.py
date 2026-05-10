"""Correlation Filter — Penalizes recently‑traded assets."""


class CorrelationFilter:
    def __init__(self, penalty_window: int = 5):
        self.penalty_window = penalty_window

    def filter(self, scored: list, cooldown) -> list:
        """
        Penalize recently traded assets by reducing their effective rank.
        Actually already handled by cooldown; this is a placeholder for
        full correlation matrix support.
        """
        return scored
