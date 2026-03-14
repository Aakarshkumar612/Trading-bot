# 🤖 Binance Futures Testnet — Trading Bot

A clean, production-style Python CLI application that places **Market**, **Limit**, and **Stop-Market** orders on the [Binance USDT-M Futures Testnet](https://testnet.binancefuture.com).

Built as part of the **Python Developer (Trading Bot)** application assessment.

---

## ✨ Features

| Feature | Details |
|---|---|
| Order types | MARKET · LIMIT · STOP_MARKET (bonus) |
| Sides | BUY · SELL |
| CLI | Typer + Rich — coloured tables, panels, validation messages |
| Auth | HMAC-SHA256 signed requests |
| Logging | Structured file + console logs (DEBUG to file, INFO to console) |
| Validation | All inputs checked before any API call |
| Error handling | API errors, network failures, and bad input all handled gracefully |
| Python | 3.12 · no external Binance SDK — pure `httpx` REST calls |

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
├── logs/
│   └── trading_bot.log      # All DEBUG+ events written here
├── .env.example             # Template for API credentials
├── .gitignore
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## ⚙️ Setup

### 1 — Prerequisites

- [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or Anaconda installed
- Python 3.12

### 2 — Create and activate a Conda environment

```bash
conda create -n trading_bot python=3.12 -y
conda activate trading_bot
```

### 3 — Clone / download the project

```bash
# Option A — clone from GitHub
git clone https://github.com/<your-username>/trading-bot.git
cd trading-bot

# Option B — unzip the submission folder
cd trading_bot
```

### 4 — Install dependencies

```bash
pip install -r requirements.txt
```

### 5 — Get Binance Futures Testnet API keys

1. Visit **https://testnet.binancefuture.com**
2. Sign in (GitHub or Google account)
3. Click your profile icon → **API Management** → **Generate API Key**
4. Copy your **API Key** and **Secret Key**

### 6 — Configure credentials

```bash
cp .env.example .env
```

Open `.env` and fill in your keys:

```env
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_SECRET_KEY=your_testnet_secret_key_here
```

> ⚠️ Never commit `.env` to Git — it is already in `.gitignore`.

---

## 🚀 Usage

All commands are run from the project root with the conda environment active.

### Place a Market order

```bash
python -m bot.cli order --symbol BTCUSDT --side BUY --type MARKET --qty 0.001
```

### Place a Limit order

```bash
python -m bot.cli order --symbol BTCUSDT --side SELL --type LIMIT --qty 0.001 --price 100000
```

### Place a Stop-Market order *(bonus)*

```bash
python -m bot.cli order --symbol BTCUSDT --side SELL --type STOP_MARKET --qty 0.001 --stop-price 95000
```

### Get help

```bash
python -m bot.cli --help
python -m bot.cli order --help
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

## 📊 Sample Output

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

╭──────────────────────────────────────────────────╮
│  Order placed successfully!                      │
│  Order ID : 3847291023                           │
│  Status   : FILLED                               │
╰──────────────────────────────────────────────────╯
```

---

## 📁 Log Files

All logs are written to `logs/trading_bot.log`.

**Log format:**
```
2025-01-15 14:23:01 | DEBUG    | client       | >> POST /fapi/v1/order | params: {...}
2025-01-15 14:23:02 | INFO     | client       | Order accepted | orderId=38472 symbol=BTCUSDT side=BUY type=MARKET status=FILLED
2025-01-15 14:23:02 | INFO     | orders       | Placing order | type=MARKET side=BUY symbol=BTCUSDT qty=0.001 price=None
```

Submitted log files:
- `logs/trading_bot.log` — contains both the market and limit order runs

---

## 🏗️ Architecture Decisions

### No `python-binance` SDK
The assessment allows direct REST calls. Using `httpx` directly keeps the dependency footprint minimal and makes the HMAC signing logic explicit and auditable.

### Layered structure
```
CLI (cli.py)  →  Validation (validators.py)  →  Order logic (orders.py)  →  API client (client.py)
```
Each layer has a single responsibility. The CLI never touches HTTP; the client never touches business logic.

### Collect-all-errors validation
`validators.py` collects every problem before raising, so users see all issues at once rather than fixing them one by one.

### Shared log file
All loggers write to a single `logs/trading_bot.log` file. This makes it easy to trace a full request lifecycle in one place — from CLI input, through validation and order construction, to the raw API response.

---

## 🧪 Assumptions

- Testnet only — base URL is hard-coded to `https://testnet.binancefuture.com`
- `timeInForce` for LIMIT orders defaults to `GTC` (Good-Till-Cancelled)
- Quantity precision is left to the user; Binance testnet is lenient about filter rules
- No position management, account queries, or order cancellation — out of scope per the brief

---

## 📦 Dependencies

| Package | Version | Purpose |
|---|---|---|
| `httpx` | ≥0.27 | Async-ready HTTP client for REST calls |
| `typer` | ≥0.12 | CLI framework built on Click |
| `rich` | ≥13.7 | Terminal formatting (tables, panels, colours) |
| `python-dotenv` | ≥1.0 | Load `.env` credentials at runtime |

---

## 👤 Author

**AAKARSH KUMAR**  
B.Tech AI — Gautam Buddha University  
