"""
app.py
------
FastAPI web server — Trading Bot UI
Run with: uvicorn app:app --reload
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from bot.client import BinanceClient, BinanceClientError
from bot.orders import place_order
from bot.validators import ValidationError
from bot.logging_config import setup_logger

load_dotenv()
logger = setup_logger("webapp")

app = FastAPI(title="Trading Bot UI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_client() -> BinanceClient:
    api_key = os.getenv("BINANCE_API_KEY", "").strip()
    secret_key = os.getenv("BINANCE_SECRET_KEY", "").strip()
    return BinanceClient(api_key=api_key, secret_key=secret_key)


@app.get("/", response_class=HTMLResponse)
async def index():
    with open("templates/index.html", "r") as f:
        return f.read()


@app.post("/api/order")
async def create_order(request: Request):
    body = await request.json()
    symbol = body.get("symbol", "").strip()
    side = body.get("side", "").strip()
    order_type = body.get("order_type", "").strip()
    quantity = float(body.get("quantity", 0))
    price = float(body.get("price")) if body.get("price") else None
    stop_price = float(body.get("stop_price")) if body.get("stop_price") else None

    logger.info("Web order request | symbol=%s side=%s type=%s qty=%s", symbol, side, order_type, quantity)

    client = get_client()
    try:
        from bot.validators import validate_inputs
        validate_inputs(symbol, side, order_type, quantity, price, stop_price)

        from bot.orders import _build_params
        params = _build_params(symbol, side, order_type, quantity, price, stop_price)
        data = client.place_order(**params)

        logger.info("Web order success | orderId=%s status=%s", data.get("orderId"), data.get("status"))
        return JSONResponse({"success": True, "data": data})

    except ValidationError as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=400)
    except BinanceClientError as e:
        return JSONResponse({"success": False, "error": e.message}, status_code=400)
    except Exception as e:
        logger.exception("Unexpected error in web order")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)
    finally:
        client.close()
        
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)        
    
from mangum import Mangum
handler = Mangum(app)    