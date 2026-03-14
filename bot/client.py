"""
client.py
---------
Low-level Binance Futures Testnet REST client.

Responsibilities:
  - HMAC-SHA256 request signing
  - HTTP execution via httpx
  - Raw request/response logging
  - HTTP & network error propagation
"""

import hashlib
import hmac
import time
from urllib.parse import urlencode

import httpx

from bot.logging_config import setup_logger

logger = setup_logger("client")

BASE_URL = "https://demo-fapi.binance.com"
_ORDER_ENDPOINT = "/fapi/v1/order"
_ALGO_ORDER_ENDPOINT = "/fapi/v1/order/oto"
_EXCHANGE_INFO_ENDPOINT = "/fapi/v1/exchangeInfo"


class BinanceClientError(Exception):
    """Raised when the Binance API returns a non-2xx response."""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(f"[{status_code}] {message}")


class BinanceClient:
    """
    Thin wrapper around the Binance USDT-M Futures Testnet REST API.

    Usage:
        client = BinanceClient(api_key="...", secret_key="...")
        response = client.place_order(symbol="BTCUSDT", side="BUY",
                                      type="MARKET", quantity=0.001)
    """

    def __init__(self, api_key: str, secret_key: str) -> None:
        self.api_key = api_key
        self._secret = secret_key.encode("utf-8")
        self._http = httpx.Client(
            base_url=BASE_URL,
            headers={"X-MBX-APIKEY": self.api_key},
            timeout=15.0,
        )
        logger.debug("BinanceClient initialised (base_url=%s)", BASE_URL)

    # ── Signing ─────────────────────────────────────────────────────────────

    def _sign(self, params: dict) -> dict:
        """Attach a server timestamp and HMAC-SHA256 signature to params."""
        params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(params)
        sig = hmac.new(self._secret, query_string.encode("utf-8"), hashlib.sha256).hexdigest()
        params["signature"] = sig
        return params

    # ── Public API ──────────────────────────────────────────────────────────

    def place_order(self, **params) -> dict:
        """
        POST /fapi/v1/order

        All Binance order parameters are forwarded as keyword arguments.
        Returns the full API response as a dict.
        """
        safe_params = {k: v for k, v in params.items()}
        logger.debug(">> POST %s | params: %s", _ORDER_ENDPOINT, safe_params)

        signed = self._sign(dict(params))

        try:
            endpoint = "/fapi/v1/order/oto" if params.get("type") == "STOP_MARKET" else _ORDER_ENDPOINT
            resp = self._http.post(endpoint, params=signed)
            logger.debug("<< %s %s", resp.status_code, resp.url)

            if not resp.is_success:
                body = resp.text
                logger.error("API error | status=%s body=%s", resp.status_code, body)
                raise BinanceClientError(resp.status_code, body)

            data: dict = resp.json()
            logger.info(
                "Order accepted | orderId=%s symbol=%s side=%s type=%s status=%s",
                data.get("orderId"),
                data.get("symbol"),
                data.get("side"),
                data.get("type"),
                data.get("status"),
            )
            logger.debug("Full response: %s", data)
            return data

        except httpx.TimeoutException:
            logger.error("Request timed out while placing order.")
            raise
        except httpx.RequestError as exc:
            logger.error("Network error: %s", exc)
            raise

    def get_symbol_info(self, symbol: str) -> dict:
        """Return exchange info for a single symbol (used by validators)."""
        try:
            resp = self._http.get(_EXCHANGE_INFO_ENDPOINT)
            resp.raise_for_status()
            symbols: list[dict] = resp.json().get("symbols", [])
            return next((s for s in symbols if s["symbol"] == symbol.upper()), {})
        except httpx.RequestError as exc:
            logger.warning("Could not fetch exchange info: %s", exc)
            return {}

    def close(self) -> None:
        self._http.close()

    # ── Context manager support ─────────────────────────────────────────────

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
