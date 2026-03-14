"""
cli.py
------
CLI entry point for the Binance Futures Testnet Trading Bot.

Usage examples:
  python -m bot.cli --symbol BTCUSDT --side BUY --type MARKET --qty 0.001
  python -m bot.cli --symbol BTCUSDT --side SELL --type LIMIT --qty 0.001 --price 100000
  python -m bot.cli --symbol BTCUSDT --side SELL --type STOP_MARKET --qty 0.001 --stop-price 95000
"""

import os
from typing import Optional

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from bot.logging_config import setup_logger
from bot.client import BinanceClient, BinanceClientError
from bot.orders import place_order
from bot.validators import ValidationError

load_dotenv()

console = Console()
logger  = setup_logger("cli")


def _get_client() -> BinanceClient:
    api_key    = os.getenv("BINANCE_API_KEY", "").strip()
    secret_key = os.getenv("BINANCE_SECRET_KEY", "").strip()

    if not api_key or not secret_key:
        console.print(
            Panel(
                "[bold red]Missing API credentials.[/bold red]\n\n"
                "Create a [yellow].env[/yellow] file in the project root with:\n"
                "  BINANCE_API_KEY=your_key\n"
                "  BINANCE_SECRET_KEY=your_secret",
                border_style="red",
                title="Configuration Error",
            )
        )
        logger.critical("API credentials not found in environment / .env")
        raise typer.Exit(code=1)

    return BinanceClient(api_key=api_key, secret_key=secret_key)


def main(
    symbol: str = typer.Option(..., "--symbol", "-s", help="Trading pair e.g. BTCUSDT"),
    side: str = typer.Option(..., "--side", help="BUY or SELL"),
    order_type: str = typer.Option(..., "--type", "-t", help="MARKET | LIMIT | STOP_MARKET"),
    quantity: float = typer.Option(..., "--qty", "-q", help="Order quantity e.g. 0.001"),
    price: Optional[float] = typer.Option(None, "--price", "-p", help="Limit price (LIMIT orders)"),
    stop_price: Optional[float] = typer.Option(None, "--stop-price", help="Stop price (STOP_MARKET orders)"),
) -> None:
    """Place an order on Binance Futures Testnet (USDT-M)."""

    logger.info(
        "CLI invoked | symbol=%s side=%s type=%s qty=%s price=%s stop_price=%s",
        symbol, side, order_type, quantity, price, stop_price,
    )

    client = _get_client()

    try:
        place_order(
            client=client,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
        )
    except ValidationError as exc:
        console.print(Panel(f"[bold red]Validation Error[/bold red]\n{exc}", border_style="red"))
        logger.error("Validation error: %s", exc)
        raise typer.Exit(code=1)
    except BinanceClientError as exc:
        console.print(Panel(f"[bold red]API Error [{exc.status_code}][/bold red]\n{exc.message}", border_style="red"))
        logger.error("API error: %s", exc)
        raise typer.Exit(code=1)
    except Exception as exc:
        console.print(Panel(f"[bold red]Unexpected Error[/bold red]\n{exc}", border_style="red"))
        logger.exception("Unhandled exception")
        raise typer.Exit(code=1)
    finally:
        client.close()


if __name__ == "__main__":
    typer.run(main)