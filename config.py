"""
Leviathan H5 - Central Configuration (boot‑safe)
=================================================
Loads from .env file, provides typed access to all settings.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── Execution Mode ──
LIVE_MODE: bool = os.getenv("LIVE_MODE", "false").lower() == "true"
TESTNET: bool = not LIVE_MODE

# ── OKX Credentials ──
OKX_API_KEY: str = os.getenv("OKX_API_KEY", "")
OKX_SECRET_KEY: str = os.getenv("OKX_SECRET_KEY", "")
OKX_PASSPHRASE: str = os.getenv("OKX_PASSPHRASE", "")

# ── Trading Parameters ──
INITIAL_CAPITAL: float = float(os.getenv("CAPITAL", "20"))
BASE_LEVERAGE: int = int(os.getenv("LEVERAGE", "5"))
TOP_N: int = int(os.getenv("TOP_N", "5"))
COOLDOWN_SEC: int = int(os.getenv("COOLDOWN", "300"))

# ── Compound Mode ──
MODE: str = os.getenv("MODE", "A").upper()

# ── Mode‑specific defaults ──
MODE_CONFIG: dict = {
    "A": {
        "reinvest_ratio": 1.0,
        "max_exposure_pct": 1.0,
        "leverage_max": 6,
        "leverage_min": 4,
        "risk_cap": 0.04,
        "kelly_fraction": 0.25,
        "dd_throttle_start": 0.05,
        "dd_throttle_max": 0.10,
    },
    "B": {
        "reinvest_ratio": 0.50,
        "max_exposure_pct": 0.40,
        "leverage_max": 4,
        "leverage_min": 2,
        "risk_cap": 0.02,
        "kelly_fraction": 0.15,
        "dd_throttle_start": 0.03,
        "dd_throttle_max": 0.07,
    },
}

# ── OKX Fees (taker) ──
TAKER_FEE: float = 0.0005

# ── Slippage Model ──
SLIPPAGE_BASE_BPS: float = 1.0
SLIPPAGE_ATR_FACTOR: float = 0.02

# ── Latency Simulation (paper mode) ──
LATENCY_MEAN_MS: float = 150
LATENCY_JITTER_MS: float = 50

# ── Exit Parameters ──
TP_ATR: float = 2.5
SL_ATR: float = 0.7
BE_ATR: float = 0.6
TRAIL_ATR: float = 1.3
TIME_DECAY_MIN: int = 180
VOL_CONTRACTION_RATIO: float = 0.7

# ── Scoring Weights ──
W_TREND: float = 0.30
W_MOMENTUM: float = 0.25
W_VOLATILITY: float = 0.25
W_VOLUME: float = 0.20
SCORE_THRESHOLD: float = 68

# ── Universe ──
MIN_VOL24H: float = 2_000_000
MAX_SPREAD_BPS: float = 10          # exclude if spread > 10 bps

# ── Persistence ──
STATE_FILE: str = "data/state.json"
TRADES_CSV: str = "data/trades.csv"
EQUITY_CSV: str = "data/equity.csv"

# 🔥 TESTNET APPROVED UNIVERSE (full CCXT symbols, ordered by historical score)
APPROVED_SYMBOLS: list = [
    "SOL/USDT:USDT", "SUI/USDT:USDT", "LINK/USDT:USDT",
    "BTC/USDT:USDT", "ETH/USDT:USDT",       # Top 5
    "OP/USDT:USDT", "ARB/USDT:USDT", "INJ/USDT:USDT",
    "LTC/USDT:USDT", "AVAX/USDT:USDT",      # Suplentes directos
    "MATIC/USDT:USDT", "DOT/USDT:USDT", "ATOM/USDT:USDT",
    "UNI/USDT:USDT", "FIL/USDT:USDT",
    "NEAR/USDT:USDT", "APT/USDT:USDT", "STX/USDT:USDT",
    "SAND/USDT:USDT", "MANA/USDT:USDT",
    "EGLD/USDT:USDT", "FTM/USDT:USDT", "GRT/USDT:USDT",
    "AXS/USDT:USDT", "WAVES/USDT:USDT",
    "ZIL/USDT:USDT", "KNC/USDT:USDT", "CVX/USDT:USDT",
    "MKR/USDT:USDT", "COMP/USDT:USDT",
]

def get_mode_config() -> dict:
    """Return active mode configuration, resolved at call time."""
    return MODE_CONFIG.get(MODE, MODE_CONFIG["A"])
