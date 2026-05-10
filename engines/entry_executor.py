# engines/entry_executor.py
"""Entry Executor — Confirms signals before execution."""
import numpy as np
import pandas as pd
from core.features import compute_features


class EntryExecutor:
    def __init__(self, confirm_timeframe: str = "3m"):
        self.confirm_tf = confirm_timeframe

    def confirm(self, exchange, symbol: str, direction: int) -> bool:
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, self.confirm_tf, limit=20)
            df = pd.DataFrame(
                ohlcv,
                columns=["ts", "open", "high", "low", "close", "vol"],
            )
            df["ts"] = pd.to_datetime(df["ts"], unit="ms")
            df.set_index("ts", inplace=True)
            df = compute_features(df)
            if df.empty:
                return False
            slope = df["slope_ema20"].iloc[-1]
            return (direction == 1 and slope > 0.001) or \
                   (direction == -1 and slope < -0.001)
        except Exception:
            return False
