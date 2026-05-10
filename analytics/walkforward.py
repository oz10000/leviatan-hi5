"""Walk‑Forward Validation — Train/test split metrics."""
import pandas as pd
import numpy as np
import os


def run_walkforward():
    csv_path = "data/trades.csv"
    if not os.path.exists(csv_path):
        return {"error": "No trade data. Run bot first."}

    df = pd.read_csv(csv_path)
    pnls = df["pnl"].dropna().values
    n = len(pnls)
    if n < 40:
        return {"error": f"Insufficient trades for W-F: {n}"}

    split = int(n * 0.7)
    train = pnls[:split]
    test = pnls[split:]

    def metrics(arr):
        wins = arr[arr > 0]
        losses = np.abs(arr[arr <= 0])
        pf = np.sum(wins) / np.sum(losses) if len(losses) > 0 else np.inf
        wr = len(wins) / len(arr) if len(arr) > 0 else 0
        sharpe = np.mean(arr) / np.std(arr) * np.sqrt(len(arr)) if np.std(arr) > 0 else 0
        return {"pf": round(float(pf), 2), "wr": round(float(wr), 3),
                "sharpe": round(float(sharpe), 2)}

    return {
        "train": metrics(train),
        "test": metrics(test),
        "degradation": {
            "sharpe": round(metrics(test)["sharpe"] / (metrics(train)["sharpe"] or 1), 2),
        },
    }
