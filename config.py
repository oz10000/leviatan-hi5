"""
Leviathan H5 - Central Configuration (boot-safe)
=================================================
Loads environment variables and exposes constants.
"""

import os
import sys

# -- Attempt to load .env (if python-dotenv is installed) --
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional

# -- Create essential directories --
for _dir in ("logs", "data"):
    os.makedirs(_dir, exist_ok=True)

# ================================================================
# 1. EXECUTION MODE
# ================================================================
LIVE_MODE: bool = os.getenv("LIVE_MODE", "false").lower() == "true"
TESTNET: bool = not LIVE_MODE

# ================================================================
# 2. OKX CREDENTIALS
# ================================================================
OKX_API_KEY: str = os.getenv("OKX_API_KEY", "")
OKX_SECRET_KEY: str = os.getenv("OKX_SECRET_KEY", "")      # unified naming
OKX_PASSPHRASE: str = os.getenv("OKX_PASSPHRASE", "")

# ================================================================
# 3. TRADING PARAMETERS
# ================================================================
INITIAL_CAPITAL: float = float(os.getenv("CAPITAL", "20"))
BASE_LEVERAGE: int = int(os.getenv("LEVERAGE", "5"))
TOP_N: int = int(os.getenv("TOP_N", "5"))
COOLDOWN_SEC: int = int(os.getenv("COOLDOWN", "300"))

# Compound mode (A = aggressive, B = defensive)
MODE: str = os.getenv("MODE", "A").upper()

# Mode-specific configurations
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

def get_mode_config() -> dict:
    """Return active mode configuration."""
    return MODE_CONFIG.get(MODE, MODE_CONFIG["A"])

# ================================================================
# 4. EXIT PARAMETERS (ATR multipliers)
# ================================================================
TP_ATR: float = 2.5
SL_ATR: float = 0.7
BE_ATR: float = 0.6
TRAIL_ATR: float = 1.3
TIME_DECAY_MIN: int = 180
VOL_CONTRACTION_RATIO: float = 0.7

# ================================================================
# 5. MARKET COSTS
# ================================================================
TAKER_FEE: float = 0.0005
SLIPPAGE_BASE_BPS: float = 1.0
SLIPPAGE_ATR_FACTOR: float = 0.02

# ================================================================
# 6. SCORING WEIGHTS
# ================================================================
W_TREND: float = 0.30
W_MOMENTUM: float = 0.25
W_VOLATILITY: float = 0.25
W_VOLUME: float = 0.20
SCORE_THRESHOLD: float = 68

# ================================================================
# 7. UNIVERSE
# ================================================================
MIN_VOL24H: float = 2_000_000
MAX_SPREAD_BPS: float = 10          # exclude if spread > 10 bps

# ================================================================
# 8. TESTNET APPROVED UNIVERSE (from simulation)
# ================================================================
# Ordered by historical Leviathan score (1m+5m, 30 days)
APPROVED_SYMBOLS: list = [
    "SOLUSDT", "SUIUSDT", "LINKUSDT", "BTCUSDT", "ETHUSDT",   # Top 5
    "OPUSDT", "ARBUSDT", "INJUSDT", "LTCUSDT", "AVAXUSDT",    # Suplentes directos
    "MATICUSDT", "DOTUSDT", "ATOMUSDT", "UNIUSDT", "FILUSDT",
    "NEARUSDT", "APTUSDT", "STXUSDT", "SANDUSDT", "MANAUSDT",
    "EGLDUSDT", "FTMUSDT", "GRTUSDT", "AXSUSDT", "WAVESUSDT",
    "ZILUSDT", "KNCUSDT", "CVXUSDT", "MKRUSDT", "COMPUSDT",
]

# ================================================================
# 9. PERSISTENCE
# ================================================================
STATE_FILE: str = "data/state.json"
TRADES_CSV: str = "data/trades.csv"
EQUITY_CSV: str = "data/equity.csv"

# ================================================================
# 10. ENVIRONMENT VALIDATION (warnings only, do not block)
# ================================================================
_issues: list = []
if not OKX_API_KEY:
    _issues.append("OKX_API_KEY is not defined")
if not OKX_SECRET_KEY:
    _issues.append("OKX_SECRET_KEY is not defined")
if LIVE_MODE and not OKX_PASSPHRASE:
    _issues.append("LIVE_MODE=True but OKX_PASSPHRASE is empty")

if _issues:
    print("[WARN] Configuration issues detected:")
    for issue in _issues:
        print(f"   - {issue}")
    print("[INFO] The bot will continue but may fail to connect to the exchange.")
