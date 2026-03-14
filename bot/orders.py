"""
orders.py
---------
Order placement logic and Rich-formatted terminal output.

Sits between the CLI layer and the API client:
  CLI → orders.place_order() → validators → client.place_order() → Binance API
"""

from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from bot.client import BinanceClient, BinanceClientError
from bot.logging_config import setup_logger
from bot.validators import validate_inputs, ValidationError

logger = setup_logger("orders")
console = Console()

# Fields we want to surface from the Binance response (in display order)
_RESPONSE_FIELDS = [
    ("orderId",      "Order ID"),
    ("symbol",       "Symbol"),
    ("status",       "Status"),
    ("type",         "Type"),
    ("side",         "Side"),
    ("origQty",      "Requested qty"),
    ("executedQty",  "Executed qty"),
    ("avgPrice",     "Avg fill price"),
    ("price",        "Limit price"),
    ("stopPrice",    "Stop price"),
    ("timeInForce",  "Time in force"),
    ("updateTime",   "Updated at"),
]


# ── Helpers ──────────────────────────────────────────────────────────────────

def _build_params(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float],
    stop_price: Optional[float],
) -> dict:
    """Construct the raw Binance order parameter dict."""
    params: dict = {
        "symbol":   symbol.upper(),
        "side":     side.upper(),
        "type":     order_type.upper(),
        "quantity": quantity,
    }

    if order_type.upper() == "LIMIT":
        params["price"] = price
        params["timeInForce"] = "GTC"  # Good-Till-Cancelled

    if order_type.upper() == "STOP_MARKET":
        params["stopPrice"] = stop_price

    return params


def _print_request_summary(params: dict) -> None:
    table = Table(
        title="📋  Order Request",
        box=box.ROUNDED,
        style="cyan",
        title_style="bold cyan",
        show_header=True,
        header_style="bold",
    )
    table.add_column("Parameter", style="bold white", min_width=18)
    table.add_column("Value",     style="yellow")

    for key, value in params.items():
        table.add_row(key, str(value))

    console.print()
    console.print(table)


def _print_response(data: dict) -> None:
    table = Table(
        title="✅  Order Response",
        box=box.ROUNDED,
        style="green",
        title_style="bold green",
        show_header=True,
        header_style="bold",
    )
    table.add_column("Field",  style="bold white", min_width=18)
    table.add_column("Value",  style="bright_green")

    for key, label in _RESPONSE_FIELDS:
        value = data.get(key)
        if value is not None and str(value) not in ("", "0", "0.00000000"):
            table.add_row(label, str(value))

    console.print()
    console.print(table)
    console.print(
        Panel(
            f"[bold green]Order placed successfully![/bold green]\n"
            f"Order ID : [yellow]{data.get('orderId')}[/yellow]\n"
            f"Status   : [cyan]{data.get('status')}[/cyan]",
            border_style="green",
        )
    )


def _print_error(message: str) -> None:
    console.print(
        Panel(f"[bold red]Order failed[/bold red]\n{message}", border_style="red")
    )


# ── Public entry point ────────────────────────────────────────────────────────

def place_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
    stop_price: Optional[float] = None,
) -> dict:
    """
    Validate inputs, build params, call the API, and print results.

    Returns the raw Binance API response dict on success.
    Raises ValidationError or BinanceClientError on failure.
    """
    # 1 — Validate
    validate_inputs(symbol, side, order_type, quantity, price, stop_price)

    # 2 — Build params
    params = _build_params(symbol, side, order_type, quantity, price, stop_price)
    logger.info(
        "Placing order | type=%s side=%s symbol=%s qty=%s price=%s",
        order_type.upper(), side.upper(), symbol.upper(), quantity, price,
    )

    # 3 — Print request summary
    _print_request_summary(params)

    # 4 — Call API
    try:
        data = client.place_order(**params)
    except (BinanceClientError, Exception) as exc:
        _print_error(str(exc))
        logger.error("Order placement failed: %s", exc)
        raise

    # 5 — Print response
    _print_response(data)
    return data
