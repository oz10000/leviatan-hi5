"""Scoring — Rank the universe by composite score."""
import pandas as pd
from core.features import compute_features
from services.logger import get_logger

logger = get_logger(__name__)


def score_universe(exchange, symbols: list) -> list:
    """Return list of (symbol, score) sorted descending."""
    results = []
    for sym in symbols:
        try:
            ohlcv = exchange.fetch_ohlcv(sym, "5m", limit=100)
            df = pd.DataFrame(
                ohlcv,
                columns=["ts", "open", "high", "low", "close", "vol"],
            )
            df["ts"] = pd.to_datetime(df["ts"], unit="ms")
            df.set_index("ts", inplace=True)
            df = compute_features(df)
            if not df.empty and len(df) >= 60:
                results.append((sym, df["score"].iloc[-1]))
        except Exception as e:
            logger.debug(f"Score error for {sym}: {e}")
    results.sort(key=lambda x: x[1], reverse=True)
    return results
