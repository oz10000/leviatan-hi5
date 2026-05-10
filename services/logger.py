"""
Professional logging — rotating files, CSV trades, structured output.
"""
import logging
import os
import csv
from datetime import datetime
from logging.handlers import RotatingFileHandler


os.makedirs("logs", exist_ok=True)
os.makedirs("data", exist_ok=True)

# ── TXT logger ──
def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter(
        "%(asctime)s.%(msecs)03d [%(levelname)-7s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    fh = RotatingFileHandler(
        "logs/bot.log", maxBytes=10 * 1024 * 1024, backupCount=5
    )
    fh.setFormatter(fmt)
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    ch.setLevel(logging.INFO)
    logger.addHandler(ch)

    return logger


# ── CSV trade log ──
TRADE_CSV = "data/trades.csv"
_CSV_INIT = not os.path.exists(TRADE_CSV)


def log_trade(symbol, direction, entry, exit_price, pnl, reason, equity):
    global _CSV_INIT
    with open(TRADE_CSV, "a", newline="") as f:
        w = csv.writer(f)
        if _CSV_INIT:
            w.writerow([
                "timestamp", "symbol", "direction", "entry", "exit",
                "pnl", "reason", "equity",
            ])
            _CSV_INIT = False
        w.writerow([
            datetime.utcnow().isoformat(),
            symbol,
            "LONG" if direction == 1 else "SHORT",
            f"{entry:.4f}",
            f"{exit_price:.4f}" if exit_price else "",
            f"{pnl:.4f}",
            reason,
            f"{equity:.4f}",
        ])
