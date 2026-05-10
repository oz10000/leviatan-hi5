"""
ASCII Console Telemetry — Low‑overhead live status display.
"""
import os
import time
from datetime import datetime


class ConsoleTelemetry:
    def __init__(self):
        self.width = 60
        try:
            self.width = os.get_terminal_size().columns
        except Exception:
            pass

    def _bar(self, label: str, value: str) -> str:
        return f"│ {label:<20} {value:>{self.width-24}} │"

    def print_header(self):
        print("┌" + "─" * (self.width - 2) + "┐")
        print(f"│{'LEVIATHAN HIGHFIVE V5':^{self.width-2}}│")
        print("├" + "─" * (self.width - 2) + "┤")

    def print_trade_open(self, sym, d, entry, sl, tp, lev, eq):
        side = "LONG" if d == 1 else "SHORT"
        print("├" + "─" * (self.width - 2) + "┤")
        print(self._bar("Signal", f"{sym} {side}"))
        print(self._bar("Entry", f"${entry:.2f}"))
        print(self._bar("Stop Loss", f"${sl:.2f}"))
        print(self._bar("Take Profit", f"${tp:.2f}"))
        print(self._bar("Leverage", f"{lev}x"))
        print(self._bar("Equity", f"${eq:.2f}"))

    def print_trade_close(self, sym, d, exit_price, pnl, eq):
        side = "LONG" if d == 1 else "SHORT"
        print(self._bar("CLOSE", f"{sym} {side}"))
        print(self._bar("Exit Price", f"${exit_price:.2f}"))
        print(self._bar("PnL", f"${pnl:+.2f}"))
        print(self._bar("Equity", f"${eq:.2f}"))
        print("├" + "─" * (self.width - 2) + "┤")

    def print_heartbeat(self, eq, peak, n_assets, trades_hr):
        dd = (peak - eq) / peak * 100 if peak > 0 else 0
        ts = datetime.utcnow().strftime("%H:%M:%S")
        status = (
            f"[{ts}] EQ=${eq:.2f} | DD={dd:.1f}% | "
            f"Assets={n_assets} | Trades/h={trades_hr}"
        )
        print(f"\r{status}", end="", flush=True)

    def print_footer(self):
        print("\n└" + "─" * (self.width - 2) + "┘")
