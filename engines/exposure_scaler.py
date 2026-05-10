"""Exposure Scaler — Reduces position sizing as drawdown increases."""


class ExposureScaler:
    def __init__(self, mode_cfg: dict):
        self.dd_start = mode_cfg.get("dd_throttle_start", 0.05)
        self.dd_max = mode_cfg.get("dd_throttle_max", 0.10)

    def scale(self, equity: float, dd: float) -> float:
        if dd <= self.dd_start:
            return 1.0
        if dd >= self.dd_max:
            return 0.3
        # Linear interpolation between start and max
        ratio = (dd - self.dd_start) / (self.dd_max - self.dd_start)
        return 1.0 - ratio * 0.7
