"""Slippage Protection — Estimates real execution price."""
import config


class SlippageProtection:
    def execution_price(self, price: float, direction: int,
                        atr_pct: float) -> float:
        base = config.SLIPPAGE_BASE_BPS / 10000
        vol_slip = config.SLIPPAGE_ATR_FACTOR * atr_pct
        total_slip = base + vol_slip
        return price * (1 + direction * total_slip)
