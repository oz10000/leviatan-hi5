"""Risk Engine — Kelly fractional, drawdown tracking, PnL history."""
import numpy as np


class RiskEngine:
    def __init__(self, kelly: float = 0.25, risk_cap: float = 0.04,
                 peak: float = 0.0):
        self.kelly = kelly
        self.risk_cap = risk_cap
        self.pnls: list = []   # pnl percentages
        self.peak = peak

    def record_pnl(self, pnl_pct: float):
        self.pnls.append(pnl_pct)
        if len(self.pnls) > 100:
            self.pnls.pop(0)

    def recent_winrate(self, window: int = 20) -> float:
        if len(self.pnls) < window:
            return 0.75  # neutral default
        recent = self.pnls[-window:]
        return sum(1 for p in recent if p > 0) / len(recent)

    def drawdown(self, equity: float) -> float:
        if self.peak <= 0:
            return 0.0
        return (self.peak - equity) / self.peak

    def kelly_risk_pct(self) -> float:
        if len(self.pnls) < 5:
            return 0.02
        wins = [p for p in self.pnls if p > 0]
        losses = [abs(p) for p in self.pnls if p <= 0]
        if not losses:
            return self.risk_cap
        avg_win = np.mean(wins)
        avg_loss = np.mean(losses)
        b = avg_win / avg_loss if avg_loss > 0 else 2.0
        p_win = len(wins) / len(self.pnls)
        f = (b * p_win - (1 - p_win)) / b if b > 0 else 0.0
        return min(self.kelly * f, self.risk_cap)
