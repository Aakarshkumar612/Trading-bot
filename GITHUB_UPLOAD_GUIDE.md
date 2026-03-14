# GitHub Upload Guide

## Step 1 — Install Git (if not already installed)

Download from https://git-scm.com/download/win and install with defaults.

Verify:
```bash
git --version
```

---

## Step 2 — Configure Git (first time only)

Open Anaconda Prompt or terminal:
```bash
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

---

## Step 3 — Create a GitHub repository

1. Go to https://github.com → click **New** (green button, top left)
2. Repository name: `trading-bot`
3. Set to **Public** (required — assessors need to see it)
4. Do NOT initialise with README (we already have one)
5. Click **Create repository**
6. Copy the HTTPS URL shown: `https://github.com/<your-username>/trading-bot.git`

---

## Step 4 — Initialise Git in your project folder

In Anaconda Prompt, navigate to your project root:
```bash
cd path\to\trading_bot
```

Then:
```bash
git init
git add .
git status          # verify .env is NOT listed (it should be ignored)
git commit -m "Initial commit: Binance Futures Testnet Trading Bot"
```

---

## Step 5 — Push to GitHub

```bash
git remote add origin https://github.com/<your-username>/trading-bot.git
git branch -M main
git push -u origin main
```

GitHub will ask for your username + a Personal Access Token (PAT).

**To create a PAT:**
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token → check **repo** scope → copy the token
3. Use the token as your password when Git asks

---

## Step 6 — Verify

Visit `https://github.com/<your-username>/trading-bot` — you should see all files including `README.md` rendered nicely.

**Checklist before sending:**
- [ ] `.env` file is NOT visible in the repo
- [ ] `logs/trading_bot.log` IS visible (contains at least one market + one limit order)
- [ ] `README.md` renders correctly
- [ ] All files in `bot/` are present

---

## Step 7 — Email submission

Send to:
- joydip@anything.ai
- chetan@anything.ai
- hello@anything.ai
- CC: sonika@anything.ai

**Subject:** `Python Developer Application — Trading Bot — [Your Name]`

**Body:**
```
Hi team,

Please find my submission for the Python Developer (Trading Bot) assessment.

GitHub repo: https://github.com/<your-username>/trading-bot

The bot supports MARKET, LIMIT, and STOP_MARKET orders on Binance Futures Testnet.
Log files from both order types are included in the logs/ folder.

Happy to discuss any part of the implementation.

Best regards,
[Your Name]
```
