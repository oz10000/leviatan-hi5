#!/usr/bin/env python3
"""
LEVIATHAN HIGHFIVE V5 — Main Production Bot
Single‑account, single‑session, modular execution engine.
"""
import time
import sys
import traceback
from datetime import datetime, timezone
from typing import Optional, Dict, List

import numpy as np
import pandas as pd

import config
from core.okx_client import OKXClientWrapper
from core.features import compute_features
from core.scoring import score_universe
from engines.trailing_stop import TrailingStop
from engines.break_even import BreakEven
from engines.risk_engine import RiskEngine
from engines.cooldown_manager import CooldownManager
from engines.session_filter import SessionFilter
from engines.dynamic_leverage import DynamicLeverage
from engines.exposure_scaler import ExposureScaler
from engines.asset_rotation import AssetRotation
from engines.loop_guardian import LoopGuardian
from engines.circuit_breaker import CircuitBreaker
from engines.correlation_filter import CorrelationFilter
from engines.slippage_protection import SlippageProtection
from state.persistence import StateManager
from risk.sizing import position_size
from monitoring.console import ConsoleTelemetry
from services.logger import get_logger, log_trade

logger = get_logger(__name__)


class LeviathanBot:
    """Main bot orchestrator. All engines are composed here."""

    def __init__(self, use_live: bool = None):
        # ── Resolve live mode ──
        if use_live is None:
            use_live = config.LIVE_MODE
        self.use_live = use_live

        # ── Exchange ──
        self.exchange = OKXClientWrapper(live=use_live)

        # ── State ──
        self.state = StateManager()
        self.equity = self.state.get("equity", config.INITIAL_CAPITAL)
        self.peak = self.state.get("peak", self.equity)

        # ── Engines ──
        mode_cfg = config.get_mode_config()
        self.trailing_stop = TrailingStop()
        self.break_even = BreakEven()
        self.risk_engine = RiskEngine(
            kelly=mode_cfg["kelly_fraction"],
            risk_cap=mode_cfg["risk_cap"],
            peak=self.peak,
        )
        self.cooldown = CooldownManager(config.COOLDOWN_SEC)
        self.session_filter = SessionFilter()
        self.dyn_lev = DynamicLeverage(mode_cfg)
        self.exposure_scaler = ExposureScaler(mode_cfg)
        self.asset_rotation = AssetRotation(top_n=config.TOP_N)
        self.loop_guardian = LoopGuardian()
        self.circuit_breaker = CircuitBreaker()
        self.corr_filter = CorrelationFilter()
        self.slippage_protection = SlippageProtection()

        # ── Position ──
        self.position: Optional[Dict] = None

        # ── Universe ──
        self.universe: List[str] = self._fetch_universe()

        # ── Console ──
        self.console = ConsoleTelemetry()

        # ── Session state ──
        self.hourly_trades: int = 0
        self.current_hour: Optional[int] = None
        self.daily_trades: int = 0
        self.current_day: Optional[int] = None

        logger.info(f"Leviathan HighFive V5 initialized | MODE={config.MODE} | "
                    f"LIVE={use_live} | Capital=${self.equity:.2f}")

    def _fetch_universe(self) -> List[str]:
        """
        Returns the tradable universe as FULL CCXT symbols.
        - Testnet: loads all available markets and intersects them with the pre‑approved list.
        - Live: filters by volume and spread.
        """
        if config.TESTNET:
            try:
                self.exchange._exchange.load_markets()
                all_markets = set(self.exchange._exchange.markets.keys())
                # Filter the approved list to only those that actually exist in testnet
                available = [sym for sym in config.APPROVED_SYMBOLS if sym in all_markets]
                logger.info(f"Testnet universe: {len(available)} of {len(config.APPROVED_SYMBOLS)} approved symbols available")
                if available:
                    return available
                # Fallback: take any swap markets available
                logger.warning("No approved symbols found in testnet markets, taking all available swaps")
                available = [s for s in all_markets if s.endswith("/USDT:USDT")]
                return available[:30]
            except Exception as e:
                logger.error(f"Failed to load testnet markets: {e}")
                return []

        # ── Live mode ──
        tickers = self.exchange.fetch_tickers()
        candidates = []
        for sym, t in tickers.items():
            if not sym.endswith("/USDT:USDT"):
                continue
            vol = t.get("quoteVolume", 0)
            if vol is None or vol < config.MIN_VOL24H:
                continue
            candidates.append((sym, vol))
        candidates.sort(key=lambda x: x[1], reverse=True)

        universe = []
        for sym, _ in candidates[:100]:
            try:
                ob = self.exchange.fetch_order_book(sym, limit=1)
                ask = ob["asks"][0][0]
                bid = ob["bids"][0][0]
                spread_bps = (ask - bid) / ask * 10000
                if spread_bps <= config.MAX_SPREAD_BPS:
                    universe.append(sym)
                    if len(universe) >= 40:
                        break
            except Exception:
                pass
        logger.info(f"Live universe: {len(universe)} tradable assets")
        return universe

    def _manage_position(self, now_ts: float) -> bool:
        """Returns True if position was closed."""
        if self.position is None:
            return False

        sym = self.position["symbol"]
        try:
            ticker = self.exchange.fetch_ticker(sym)
            price = ticker["last"]
        except Exception as e:
            logger.warning(f"Ticker fetch failed for {sym}: {e}")
            return False

        atr = self.position["atr"]

        # Update engines
        self.position = self.trailing_stop.update(self.position, price, atr)
        self.position = self.break_even.apply(self.position, price, atr)

        # Check exit
        d = self.position["dir"]
        exit_price = None
        exit_reason = ""

        if d == 1:
            if price <= self.position["trail_sl"]:
                exit_price = self.position["trail_sl"]
                exit_reason = "trailing_sl"
            elif price >= self.position.get("tp", 9e9):
                exit_price = self.position["tp"]
                exit_reason = "tp"
        else:
            if price >= self.position["trail_sl"]:
                exit_price = self.position["trail_sl"]
                exit_reason = "trailing_sl"
            elif price <= self.position.get("tp", -9e9):
                exit_price = self.position["tp"]
                exit_reason = "tp"

        if exit_price:
            pnl = ((exit_price - self.position["entry"]) * d
                   * self.position["leverage"] * self.position["size"]
                   / self.position["entry"])
            pnl -= self.position["size"] * self.position["entry"] * config.TAKER_FEE * 2

            self.equity += pnl
            self.peak = max(self.peak, self.equity)

            pnl_pct = pnl / (self.equity - pnl) if self.equity != pnl else 0.0
            self.risk_engine.record_pnl(pnl_pct)

            log_trade(sym, d, self.position["entry"], exit_price, pnl,
                      exit_reason, self.equity)
            self.console.print_trade_close(sym, d, exit_price, pnl, self.equity)

            self.state.save(equity=self.equity, peak=self.peak)
            self.cooldown.record(sym)
            self.position = None
            return True

        return False

    def _open_position(self, now_ts: float):
        """Scan universe, score, rank, and open best trade."""
        # Hour/day tracking for rate limits
        dt = datetime.fromtimestamp(now_ts, tz=timezone.utc)
        if self.current_hour != dt.hour:
            self.current_hour = dt.hour
            self.hourly_trades = 0
        if self.current_day != dt.day:
            self.current_day = dt.day
            self.daily_trades = 0

        if self.hourly_trades >= 6:
            return  # rate limit
        if self.daily_trades >= 30:
            return

        # Session filter
        allowed, exposure_factor = self.session_filter.check()
        if not allowed:
            logger.info("Session blocked by filter")
            return

        # Circuit breaker
        if self.circuit_breaker.is_triggered(self.equity, self.peak):
            logger.warning("Circuit breaker active — skipping trade")
            return

        # ── Build candidate list ──
        # In testnet the universe is already ordered by historical score.
        if config.TESTNET:
            eligible = [sym for sym in self.universe if self.cooldown.can_trade(sym)]
        else:
            ranked = score_universe(self.exchange, self.universe)
            ranked = self.corr_filter.filter(ranked, self.cooldown)
            eligible = [sym for sym, _ in ranked if self.cooldown.can_trade(sym)]

        if not eligible:
            return

        # Select best eligible (top 5 priority, then suplentes)
        for sym in eligible:
            # Fetch features
            try:
                ohlcv_5m = self.exchange.fetch_ohlcv(sym, "5m", limit=100)
                df = pd.DataFrame(
                    ohlcv_5m,
                    columns=["ts", "open", "high", "low", "close", "vol"],
                )
                df["ts"] = pd.to_datetime(df["ts"], unit="ms")
                df.set_index("ts", inplace=True)
                df = compute_features(df)
                if df.empty or len(df) < 60:
                    continue
                row = df.iloc[-1]
            except Exception as e:
                logger.debug(f"Feature error {sym}: {e}")
                continue

            # Direction
            direction = 1 if row["ema20"] > row["ema50"] else -1

            # ATR
            atr = row["atr"]
            if atr <= 0 or np.isnan(atr):
                continue
            price = row["close"]
            atr_pct = row["atr_pct"]

            # Dynamic leverage
            dd = (self.peak - self.equity) / self.peak if self.peak > 0 else 0.0
            recent_wr = self.risk_engine.recent_winrate()
            leverage = self.dyn_lev.calculate(recent_wr, dd)

            # Exposure scaling
            exposure_factor *= self.exposure_scaler.scale(self.equity, dd)

            # Position size — professional sizing
            size = position_size(
                equity=self.equity,
                price=price,
                atr=atr,
                atr_pct=atr_pct,
                direction=direction,
                leverage=leverage,
                risk_cap=config.get_mode_config()["risk_cap"],
                exposure_factor=exposure_factor,
            )
            if size <= 0:
                continue

            # Slippage-aware execution
            exec_price = self.slippage_protection.execution_price(
                price, direction, atr_pct
            )

            # Open position
            tp = exec_price + direction * config.TP_ATR * atr
            sl = exec_price - direction * config.SL_ATR * atr

            self.position = {
                "symbol": sym,
                "dir": direction,
                "entry": exec_price,
                "atr": atr,
                "atr_pct_entry": atr_pct,
                "size": size,
                "leverage": leverage,
                "sl": sl,
                "trail_sl": sl,
                "tp": tp,
                "be_done": False,
                "trail_activated": False,
                "entry_time": now_ts,
            }

            self.cooldown.record(sym)
            self.hourly_trades += 1
            self.daily_trades += 1

            log_trade(sym, direction, exec_price, None, 0.0, "open", self.equity)
            self.console.print_trade_open(sym, direction, exec_price, sl,
                                          tp, leverage, self.equity)
            self.state.save(equity=self.equity, peak=self.peak)
            break

    def run(self):
        """Main execution loop."""
        self.loop_guardian.acquire()

        logger.info("=" * 60)
        logger.info("LEVIATHAN HIGHFIVE V5 — Starting main loop")
        logger.info("=" * 60)
        self.console.print_header()

        try:
            while True:
                now_ts = time.time()

                # ── Manage open position ──
                closed = self._manage_position(now_ts)
                if closed:
                    time.sleep(2)
                    continue

                # ── Open new position if none ──
                if self.position is None:
                    self._open_position(now_ts)

                # ── Heartbeat ──
                self.console.print_heartbeat(
                    self.equity, self.peak,
                    len(self.universe), self.hourly_trades,
                )

                # ── Save state periodically ──
                self.state.save(equity=self.equity, peak=self.peak)

                time.sleep(30)

        except KeyboardInterrupt:
            logger.info("Shutdown signal received")
        except Exception as e:
            logger.critical(f"Fatal error: {e}\n{traceback.format_exc()}")
        finally:
            self.loop_guardian.release()
            self.state.save(equity=self.equity, peak=self.peak)
            logger.info("Bot stopped gracefully")


if __name__ == "__main__":
    bot = LeviathanBot()
    bot.run()
