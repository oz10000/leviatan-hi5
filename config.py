"""
Leviathan H5 – Configuration (boot‑safe)
=========================================
Carga variables de entorno y proporciona valores por defecto
para la ejecución mínima en testnet.
"""
import os
import sys

# ── Asegurar existencia de directorios necesarios ──
for _dir in ("logs", "data"):
    os.makedirs(_dir, exist_ok=True)

# ── Modo de ejecución ──
LIVE_MODE = os.getenv("LIVE_MODE", "false").lower() == "true"

# ── Credenciales OKX ──
OKX_API_KEY = os.getenv("OKX_API_KEY", "")
OKX_SECRET_KEY = os.getenv("OKX_API_SECRET", "")  # también usado como OKX_API_SECRET
OKX_PASSPHRASE = os.getenv("OKX_PASSPHRASE", "")

# ── Configuración de testnet / live ──
TESTNET = not LIVE_MODE

# ── Parámetros de trading (mínimos, pueden sobrescribirse en main.py) ──
INITIAL_CAPITAL = 20.0
BASE_LEVERAGE = 5
TOP_N = 5
COOLDOWN_SEC = 300

# ── Gestión de riesgo ──
KELLY_FRACTION = 0.25
RISK_CAP = 0.04
MAX_DD_LIMIT = 0.15

# ── Salida (ATR multipliers) ──
TP_ATR = 2.5
SL_ATR = 0.7
BE_ATR = 0.6
TRAIL_ATR = 1.3
TIME_DECAY_MIN = 180
VOL_CONTRACTION_RATIO = 0.7

# ── Comisiones y slippage ──
TAKER_FEE = 0.0005
SLIPPAGE_BASE_BPS = 1.0
SLIPPAGE_ATR_FACTOR = 0.02

# ── Scoring weights ──
W_TREND = 0.30
W_MOMENTUM = 0.25
W_VOLATILITY = 0.25
W_VOLUME = 0.20

# ── Universo ──
MIN_VOL24H = 2_000_000
MAX_SPREAD_BPS = 10

# ── Persistencia ──
STATE_FILE = "data/state.json"
TRADES_CSV = "data/trades.csv"
EQUITY_CSV = "data/equity.csv"

# ── Validaciones mínimas ──
issues = []
if not OKX_API_KEY:
    issues.append("OKX_API_KEY no está definida")
if not OKX_SECRET_KEY:
    issues.append("OKX_API_SECRET no está definida")
if LIVE_MODE and not OKX_PASSPHRASE:
    issues.append("LIVE_MODE=True pero OKX_PASSPHRASE está vacía")

if issues:
    print("[WARN] Problemas de configuración detectados:")
    for issue in issues:
        print(f"   - {issue}")
    print("[INFO] El bot continuará pero puede fallar al conectarse al exchange.")

# ── Compatibilidad con modo A/B (se usará en main.py) ──
MODE = os.getenv("MODE", "A").upper()
MODE_CONFIG = {
    "A": {"reinvest_ratio": 1.0, "max_exposure_pct": 1.0, "leverage_max": 6, "leverage_min": 4, "risk_cap": 0.04, "kelly_fraction": 0.25, "dd_throttle_start": 0.05, "dd_throttle_max": 0.10},
    "B": {"reinvest_ratio": 0.50, "max_exposure_pct": 0.40, "leverage_max": 4, "leverage_min": 2, "risk_cap": 0.02, "kelly_fraction": 0.15, "dd_throttle_start": 0.03, "dd_throttle_max": 0.07}
}
