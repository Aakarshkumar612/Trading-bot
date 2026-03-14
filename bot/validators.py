"""
validators.py
-------------
Input validation for CLI arguments before any API call is made.

All validation errors are collected and raised together so the user
sees every problem in a single message instead of fixing them one by one.
"""

from bot.logging_config import setup_logger

logger = setup_logger("validators")

VALID_SIDES: frozenset[str] = frozenset({"BUY", "SELL"})
VALID_ORDER_TYPES: frozenset[str] = frozenset({"MARKET", "LIMIT", "STOP_MARKET"})

# Minimum sane quantity — Binance testnet typically requires >= 0.001 BTC
_MIN_QUANTITY = 1e-8
_MAX_SYMBOL_LEN = 20


class ValidationError(ValueError):
    """Raised when one or more user inputs fail validation."""


def validate_inputs(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: float | None,
    stop_price: float | None = None,
) -> None:
    """
    Validate all order parameters and raise ValidationError if any are invalid.

    Parameters
    ----------
    symbol      : e.g. "BTCUSDT"
    side        : "BUY" or "SELL"
    order_type  : "MARKET", "LIMIT", or "STOP_MARKET"
    quantity    : positive float
    price       : required for LIMIT orders; must be positive
    stop_price  : required for STOP_MARKET orders; must be positive
    """
    errors: list[str] = []

    # ── Normalise ────────────────────────────────────────────────────────────
    symbol_up = symbol.strip().upper()
    side_up = side.strip().upper()
    type_up = order_type.strip().upper()

    # ── Symbol ───────────────────────────────────────────────────────────────
    if not symbol_up:
        errors.append("Symbol cannot be empty.")
    elif not symbol_up.isalnum():
        errors.append(f"Symbol '{symbol_up}' must be alphanumeric (e.g. BTCUSDT, ETHUSDT).")
    elif len(symbol_up) > _MAX_SYMBOL_LEN:
        errors.append(f"Symbol '{symbol_up}' is too long (max {_MAX_SYMBOL_LEN} chars).")

    # ── Side ─────────────────────────────────────────────────────────────────
    if side_up not in VALID_SIDES:
        errors.append(f"Side '{side_up}' is invalid. Choose BUY or SELL.")

    # ── Order type ───────────────────────────────────────────────────────────
    if type_up not in VALID_ORDER_TYPES:
        errors.append(
            f"Order type '{type_up}' is invalid. "
            f"Choose one of: {', '.join(sorted(VALID_ORDER_TYPES))}."
        )

    # ── Quantity ─────────────────────────────────────────────────────────────
    if quantity < _MIN_QUANTITY:
        errors.append(f"Quantity must be >= {_MIN_QUANTITY}. Got: {quantity}.")

    # ── Price (LIMIT) ─────────────────────────────────────────────────────────
    if type_up == "LIMIT":
        if price is None:
            errors.append("--price is required for LIMIT orders.")
        elif price <= 0:
            errors.append(f"Price must be positive for LIMIT orders. Got: {price}.")

    # ── Stop price (STOP_MARKET) ──────────────────────────────────────────────
    if type_up == "STOP_MARKET":
        if stop_price is None:
            errors.append("--stop-price is required for STOP_MARKET orders.")
        elif stop_price <= 0:
            errors.append(f"Stop price must be positive. Got: {stop_price}.")

    # ── Report ───────────────────────────────────────────────────────────────
    if errors:
        for err in errors:
            logger.warning("Validation failed: %s", err)
        raise ValidationError("\n  • ".join([""] + errors))

    logger.debug(
        "Validation passed | symbol=%s side=%s type=%s qty=%s price=%s stop_price=%s",
        symbol_up, side_up, type_up, quantity, price, stop_price,
    )
