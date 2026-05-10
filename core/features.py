"""
Feature Engine — All technical indicators.
CRITICAL: All rolling computations use .shift(1) to prevent lookahead.
"""
import numpy as np
import pandas as pd


def compute_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # ── Basic ──
    df["prev_close"] = df["close"].shift(1)

    # ── True Range & ATR (shifted) ──
    df["tr"] = np.maximum(
        df["high"] - df["low"],
        np.maximum(
            abs(df["high"] - df["prev_close"]),
            abs(df["low"] - df["prev_close"]),
        ),
    )
    df["atr"] = df["tr"].rolling(14).mean().shift(1)  # ← prevents lookahead
    df["atr_pct"] = df["atr"] / df["close"]

    # ── EMAs ──
    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
    df["slope_ema20"] = (
        df["ema20"].diff(5) / df["ema20"].shift(5)
    ).shift(1)

    # ── Volume ──
    df["volume_avg"] = df["vol"].rolling(20).mean().shift(1)
    df["volume_ratio"] = df["vol"] / df["volume_avg"]

    # ── Momentum (shifted) ──
    df["momentum"] = df["close"].pct_change(5).shift(1)

    # ── Sub‑scores (0–100) ──
    df["trend_score"] = np.where(
        (df["ema20"] > df["ema50"]) & (df["slope_ema20"] > 0), 100,
        np.where((df["ema20"] > df["ema50"]) & (df["slope_ema20"] <= 0), 70,
                 np.where((df["ema20"] < df["ema50"]) & (df["slope_ema20"] < 0), 0, 30)),
    )
    df["volatility_score"] = (
        100 - np.abs(df["atr_pct"] - 0.01) * 10000
    ).clip(0, 100)
    df["volume_score"] = ((df["volume_ratio"].clip(0.5, 2) - 0.5) / 1.5 * 100)
    df["momentum_score"] = (
        df["momentum"].rolling(50).rank(pct=True).shift(1) * 100
    )  # ← prevents lookahead

    # ── Composite Score ──
    df["score"] = (
        0.30 * df["trend_score"]
        + 0.25 * df["momentum_score"]
        + 0.25 * df["volatility_score"]
        + 0.20 * df["volume_score"]
    )

    return df.dropna()
