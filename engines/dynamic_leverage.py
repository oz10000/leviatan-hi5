"""Dynamic Leverage — Adjusts leverage based on recent winrate and drawdown."""


class DynamicLeverage:
    def __init__(self, mode_cfg: dict):
        self.base = mode_cfg.get("leverage_max", 5)
        self.min_lev = mode_cfg.get("leverage_min", 4)
        self.current = self.base

    def calculate(self, recent_winrate: float, dd: float) -> int:
        if dd > 0.10:
            self.current = max(self.min_lev, self.base - 2)
        elif dd > 0.05:
            self.current = max(self.min_lev, self.base - 1)
        elif recent_winrate > 0.82 and dd < 0.02:
            self.current = min(self.base + 1, 6)
        else:
            self.current = self.base
        return int(self.current)
