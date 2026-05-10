"""Monte Carlo Simulation — Bootstrap trades to assess robustness."""
import numpy as np
import pandas as pd
import os


def run_monte_carlo(num_runs: int = 2000):
    csv_path = "data/trades.csv"
    if not os.path.exists(csv_path):
        return {"error": "No trade data. Run bot first."}

    df = pd.read_csv(csv_path)
    pnls = df["pnl"].dropna().values
    if len(pnls) < 20:
        return {"error": f"Insufficient trades: {len(pnls)}"}

    rng = np.random.default_rng(42)
    results = []
    for _ in range(num_runs):
        shuffled = rng.permutation(pnls)
        equity = np.cumsum(shuffled) + float(df["equity"].iloc[0])
        peak = np.maximum.accumulate(equity)
        dd = (peak - equity) / peak
        results.append({
            "final_equity": equity[-1],
            "max_dd": float(np.max(dd)),
        })

    finals = [r["final_equity"] for r in results]
    dds = [r["max_dd"] for r in results]

    return {
        "equity_mean": float(np.mean(finals)),
        "equity_p5": float(np.percentile(finals, 5)),
        "equity_p95": float(np.percentile(finals, 95)),
        "dd_mean": float(np.mean(dds)),
        "dd_p95": float(np.percentile(dds, 95)),
        "ruin_probability": float(np.mean([1 if f < 3 else 0 for f in finals])),
    }
