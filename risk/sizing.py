"""
Professional Position Sizing — Risk‑based, ATR‑aware, liquidation‑safe.

sizing = (equity × risk_pct × leverage) / (stop_distance_in_price)

stop_distance = max(SL_ATR_mult × ATR, min_slippage_buffer)

This ensures risk is constant in USD terms regardless of asset volatility.
"""
import numpy as np
import config


def position_size(
    equity: float,
    price: float,
    atr: float,
    atr_pct: float,
    direction: int,
    leverage: int,
    risk_cap: float,
    exposure_factor: float = 1.0,
) -> float:
    """
    Compute position size in contracts based on monetary risk.

    Args:
        equity:      current portfolio equity
        price:       entry price
        atr:         ATR(14) in price units
        atr_pct:     ATR as percentage of price
        direction:   1 for long, -1 for short
        leverage:    current leverage multiplier
        risk_cap:    maximum fraction of equity to risk per trade
        exposure_factor: multiplier from session/exposure scaling (0–1)

    Returns:
        Position size in contracts (units of base asset)
    """

    # ── 1. Stop distance in price terms ──
    # SL_ATR * ATR gives the base stop distance; add slippage buffer
    slippage_buffer = (config.SLIPPAGE_BASE_BPS / 10000) * price
    volatility_buffer = config.SLIPPAGE_ATR_FACTOR * atr
    stop_distance = config.SL_ATR * atr + slippage_buffer + volatility_buffer

    # ── 2. Monetary risk per trade ──
    risk_capital = equity * risk_cap * exposure_factor

    # ── 3. Risk per contract = stop_distance / price (fraction of price) × price × leverage ──
    risk_per_contract = (stop_distance / price) * price * leverage

    if risk_per_contract <= 0:
        return 0.0

    # ── 4. Position size ──
    size = risk_capital / risk_per_contract

    # ── 5. Cap by liquidation distance ──
    # Ensure we're not too close to liquidation
    liq_distance = price * 0.05  # 5% minimum buffer
    max_size_liq = equity * 0.90 / (liq_distance * leverage / price)
    size = min(size, max_size_liq)

    # ── 6. Floor and sanity ──
    if size <= 0 or np.isnan(size) or np.isinf(size):
        return 0.0

    return float(size)
