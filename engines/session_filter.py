"""
Session Filter — Blocks trading during statistically unfavorable periods.

Analysis showed:
- Weekends: higher slippage, lower winrate
- Futures expiry (last Fri of month): extreme volatility
- Major macro events: avoid (CPI, FOMC, NFP)
"""
from datetime import datetime, timezone


class SessionFilter:
    # Hours to block before/after major events (UTC)
    EVENT_BLOCK_HOURS: int = 1

    def __init__(self):
        self._macro_dates = self._load_macro_calendar()

    def _load_macro_calendar(self) -> set:
        """Simple macro event calendar — expand as needed."""
        # Format: (year, month, day)
        return set()

    def check(self) -> tuple:
        """
        Returns (allowed: bool, exposure_multiplier: float).
        """
        now = datetime.now(timezone.utc)
        wd = now.weekday()

        # ── Weekends ──
        if wd == 5:  # Saturday
            return True, 0.70
        if wd == 6:  # Sunday
            return True, 0.50

        # ── Futures expiry (last Friday of month) ──
        if wd == 4 and now.day >= 25:
            return False, 0.0

        # ── Macro events ──
        for yr, mo, dy in self._macro_dates:
            if now.year == yr and now.month == mo and now.day == dy:
                if abs((now.hour + now.minute / 60) - 13.5) <= self.EVENT_BLOCK_HOURS:
                    return False, 0.0

        # ── Normal operation ──
        return True, 1.0
