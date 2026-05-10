"""
OKX Client Wrapper — ccxt-based with retry, reconnect, and
testnet/live auto‑detection. Uses x-simulated-trading header for demo.
"""
import time
import ccxt
import config
from services.logger import get_logger

logger = get_logger(__name__)


class OKXClientWrapper:
    def __init__(self, live: bool = False):
        headers = {}
        if not live:
            headers["x-simulated-trading"] = "1"

        self._exchange = ccxt.okx({
            "apiKey": config.OKX_API_KEY,
            "secret": config.OKX_API_SECRET,
            "password": config.OKX_PASSPHRASE,
            "enableRateLimit": True,
            "options": {
                "defaultType": "swap",
            },
            "headers": headers,
        })

        if not live:
            self._exchange.set_sandbox_mode(True)

        self.live = live
        self.max_retries = 3
        self.retry_delay = 2.0

    def _retry(self, fn, *args, **kwargs):
        """Generic retry wrapper."""
        last_err = None
        for attempt in range(self.max_retries):
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                last_err = e
                logger.warning(f"Attempt {attempt+1}/{self.max_retries} failed: {e}")
                time.sleep(self.retry_delay * (attempt + 1))
        raise last_err

    def fetch_tickers(self):
        return self._retry(self._exchange.fetch_tickers)

    def fetch_ohlcv(self, symbol: str, timeframe: str = "5m", limit: int = 100):
        inst = f"{symbol}/USDT:USDT"
        return self._retry(self._exchange.fetch_ohlcv, inst, timeframe, limit=limit)

    def fetch_ticker(self, symbol: str):
        inst = f"{symbol}/USDT:USDT"
        return self._retry(self._exchange.fetch_ticker, inst)

    def fetch_order_book(self, symbol: str, limit: int = 5):
        inst = f"{symbol}/USDT:USDT"
        return self._retry(self._exchange.fetch_order_book, inst, limit)

    def fetch_balance(self):
        return self._retry(self._exchange.fetch_balance)

    def create_order(self, symbol, order_type, side, amount):
        inst = f"{symbol}/USDT:USDT"
        return self._retry(
            self._exchange.create_order, inst, order_type, side, amount
        )
