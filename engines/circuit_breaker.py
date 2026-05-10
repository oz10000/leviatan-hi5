"""Circuit Breaker — Halts trading on extreme drawdown or consecutive losses."""


class CircuitBreaker:
    def __init__(self):
        self.max_dd = 0.15        # 15% max drawdown
        self.max_consecutive = 8   # consecutive losing trades

    def is_triggered(self, equity: float, peak: float,
                     consecutive_losses: int = 0) -> bool:
        dd = (peak - equity) / peak if peak > 0 else 0
        if dd >= self.max_dd:
            return True
        if consecutive_losses >= self.max_consecutive:
            return True
        return False
