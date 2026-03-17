# 🤖 Binance Futures Testnet — Trading Bot

A clean, production-style **FastAPI web application** that places **Market**, **Limit**, and **Stop-Market** orders on the [Binance USDT-M Futures Testnet](https://testnet.binancefuture.com).

🌐 **Live Demo:** [https://trading-bot-oja7.onrender.com](https://trading-bot-oja7.onrender.com)

Built as part of the **Python Developer (Trading Bot)** application assessment.

---

## ✨ Features

| Feature | Details |
|---|---|
| Order types | MARKET · LIMIT · STOP_MARKET (bonus) |
| Sides | BUY · SELL |
| Web UI | Clean HTML/CSS frontend served via FastAPI |
| API | REST endpoints via FastAPI + uvicorn |
| Auth | HMAC-SHA256 signed requests |
| Logging | Structured file + console logs (DEBUG to file, INFO to console) |
| Validation | All inputs checked before any API call |
| Error handling | API errors, network failures, and bad input all handled gracefully |
| Python | 3.12 · no external Binance SDK — pure `httpx` REST calls |
| Deployed | Render (free tier) |

---

## 🗂️ Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py          # Package marker
│   ├── cli.py               # CLI entry point (Typer)
│   ├── client.py            # Binance REST client (HMAC signing, httpx)
│   ├── orders.py            # Order logic + Rich output formatting
│   ├── validators.py        # Input validation (all errors collected at once)
│   └── logging_config.py   # Shared logger (file + console handlers)
├── templates/
│   └── index.html           # Web UI frontend
├── logs/
│   └── trading_bot.log      # All DEBUG+ events written here
├── .env.example             # Template for API credentials
├── .gitignore
├── app.py                   # FastAPI web server entry point
├── render.yaml              # Render deployment config
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## 🌐 Web App (Live)

The bot is deployed and accessible at:

**[https://trading-bot-oja7.onrender.com](https://trading-bot-oja7.onrender.com)**

> ⚠️ Hosted on Render's free tier — the service spins down after 15 minutes of inactivity.
> First request may take ~30 seconds to wake up. Subsequent requests are instant.

### API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Web UI |
| `POST` | `/api/order` | Place an order |

### POST `/api/order` — Request Body

```json
{
  "symbol": "BTCUSDT",
  "side": "BUY",
  "order_type": "MARKET",
  "quantity": 0.001,
  "price": null,
  "stop_price": null
}
```

### POST `/api/order` — Response

```json
{
  "success": true,
  "data": {
    "orderId": 3847291023,
    "symbol": "BTCUSDT",
    "status": "FILLED",
    "type": "MARKET",
    "side": "BUY",
    "origQty": "0.001",
    "executedQty": "0.001",
    "avgPrice": "67432.10"
  }
}
```

---

## ⚙️ Local Setup

### 1 — Prerequisites

- [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or Anaconda
- Python 3.12

### 2 — Clone the repository

```bash
git clone https://github.com/Aakarshkumar612/Trading-bot.git
cd Trading-bot
```

### 3 — Create and activate Conda environment

```bash
conda create -n trading_bot python=3.12 -y
conda activate trading_bot
```

### 4 — Install dependencies

```bash
pip install -r requirements.txt
```

### 5 — Get Binance Futures Testnet API keys

1. Visit **[https://testnet.binancefuture.com](https://testnet.binancefuture.com)**
2. Sign in with GitHub or Google
3. Click profile → **API Management** → **Generate API Key**
4. Copy your **API Key** and **Secret Key**

### 6 — Configure credentials

```bash
cp .env.example .env
```

Open `.env` and fill in:

```env
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_SECRET_KEY=your_testnet_secret_key_here
```

> ⚠️ Never commit `.env` to Git — it is already in `.gitignore`.

### 7 — Run locally

```bash
uvicorn app:app --reload
```

Open **[http://localhost:8000](http://localhost:8000)** in your browser.

---

## 💻 CLI Usage (Alternative)

You can also place orders directly from the terminal:

```bash
# Market order
python -m bot.cli order --symbol BTCUSDT --side BUY --type MARKET --qty 0.001

# Limit order
python -m bot.cli order --symbol BTCUSDT --side SELL --type LIMIT --qty 0.001 --price 100000

# Stop-Market order (bonus)
python -m bot.cli order --symbol BTCUSDT --side SELL --type STOP_MARKET --qty 0.001 --stop-price 95000
```

---

## 📋 CLI Options Reference

| Option | Short | Required | Description |
|---|---|---|---|
| `--symbol` | `-s` | ✅ | Trading pair (e.g. `BTCUSDT`, `ETHUSDT`) |
| `--side` | | ✅ | `BUY` or `SELL` |
| `--type` | `-t` | ✅ | `MARKET`, `LIMIT`, or `STOP_MARKET` |
| `--qty` | `-q` | ✅ | Order quantity (e.g. `0.001`) |
| `--price` | `-p` | LIMIT only | Limit price |
| `--stop-price` | | STOP_MARKET only | Stop trigger price |

---

## 📊 Sample CLI Output

```
╭─────────────── 📋  Order Request ────────────────╮
│ Parameter          │ Value                        │
│ symbol             │ BTCUSDT                      │
│ side               │ BUY                          │
│ type               │ MARKET                       │
│ quantity           │ 0.001                        │
╰──────────────────────────────────────────────────╯

╭─────────────── ✅  Order Response ───────────────╮
│ Field              │ Value                        │
│ Order ID           │ 3847291023                   │
│ Symbol             │ BTCUSDT                      │
│ Status             │ FILLED                       │
│ Type               │ MARKET                       │
│ Side               │ BUY                          │
│ Requested qty      │ 0.001                        │
│ Executed qty       │ 0.001                        │
│ Avg fill price     │ 67432.10                     │
╰──────────────────────────────────────────────────╯
```

---

## 🚀 Deployment

This app is deployed on **[Render](https://render.com)** using `render.yaml`:

```yaml
services:
  - type: web
    name: trading-bot
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: BINANCE_API_KEY
        sync: false
      - key: BINANCE_SECRET_KEY
        sync: false
```

To deploy your own instance:
1. Fork this repository
2. Sign up at [render.com](https://render.com) with GitHub
3. Create a new **Web Service** → connect your fork
4. Add `BINANCE_API_KEY` and `BINANCE_SECRET_KEY` as environment variables
5. Deploy — Render auto-deploys on every `git push` ✅

---

## 🏗️ Architecture

```
Browser / CLI
     │
     ▼
FastAPI (app.py)
     │
     ├── GET  /          → serves templates/index.html
     └── POST /api/order
               │
               ▼
        validators.py   ← collect all input errors at once
               │
               ▼
          orders.py     ← build order params
               │
               ▼
          client.py     ← HMAC-SHA256 sign + httpx POST to Binance Testnet
```

### Key decisions

- **No `python-binance` SDK** — pure `httpx` keeps dependencies minimal and HMAC signing explicit
- **Collect-all-errors validation** — users see every problem at once, not one at a time
- **Single log file** — full request lifecycle traceable in one place
- **Render deployment** — zero-config, free tier, auto-deploys on every `git push`

---

## 📦 Dependencies

| Package | Version | Purpose |
|---|---|---|
| `fastapi` | ≥0.110 | Web framework |
| `uvicorn` | ≥0.29 | ASGI server |
| `httpx` | ≥0.27 | HTTP client for Binance REST calls |
| `typer` | ≥0.12 | CLI framework |
| `rich` | ≥13.7 | Terminal formatting |
| `python-dotenv` | ≥1.0 | Load `.env` credentials |

---

## 📁 Logs

All logs written to `logs/trading_bot.log`:

```
2025-01-15 14:23:01 | DEBUG | client | >> POST /fapi/v1/order | params: {...}
2025-01-15 14:23:02 | INFO  | client | Order accepted | orderId=38472 status=FILLED
2025-01-15 14:23:02 | INFO  | orders | Placing order | type=MARKET side=BUY qty=0.001
```

---

## 🧪 Assumptions

- Testnet only — base URL hard-coded to `https://testnet.binancefuture.com`
- `timeInForce` for LIMIT orders defaults to `GTC` (Good-Till-Cancelled)
- No position management, account queries, or order cancellation — out of scope

---

## 👤 Author

**Aakarsh Kumar**
B.Tech Artificial Intelligence — Gautam Buddha University
GitHub: [Aakarshkumar612](https://github.com/Aakarshkumar612)