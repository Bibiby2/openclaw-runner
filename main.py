import os
import time
import requests
from datetime import datetime

# ========================
# ENV
# ========================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("OPENWEATHER_API_KEY")

# ========================
# SETTINGS
# ========================
CITIES = ["London", "New York", "Hong Kong"]

BET_AMOUNT = 2
EDGE_THRESHOLD = 20   # nur starke Trades
COOLDOWN = 300       # 5 Minuten pro Stadt
MAX_TRADES_PER_RUN = 2

# ========================
# STATE
# ========================
portfolio = {
    "balance": 100.0,
    "wins": 0,
    "losses": 0,
    "trades": []
}

LAST_TRADE_TIME = {}

# ========================
# TELEGRAM
# ========================
def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        print("Telegram Error")

# ========================
# WEATHER API
# ========================
def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    r = requests.get(url)
    return r.json()

# ========================
# MODEL (REALISTIC)
# ========================
def calculate_model(weather):
    try:
        rain = weather.get("rain", {}).get("1h", 0)
        clouds = weather["clouds"]["all"]
        humidity = weather["main"]["humidity"]
        wind = weather["wind"]["speed"]

        score = 0

        # Regen (stärker gewichtet)
        if rain > 0:
            score += min(rain * 10, 30)

        # Wolken
        score += (clouds / 100) * 25

        # Luftfeuchtigkeit
        score += (humidity / 100) * 25

        # Wind Bonus
        if wind > 8:
            score += 10

        return round(min(score, 85), 2)

    except:
        return 0

# ========================
# MARKET (SIMULATION)
# ========================
def get_market_probability():
    return round(40 + (20 * (time.time() % 1)), 2)

# ========================
# PAPER TRADE
# ========================
def place_paper_trade(city, model, market):
    global LAST_TRADE_TIME

    now = time.time()

    # Cooldown Check
    if city in LAST_TRADE_TIME:
        if now - LAST_TRADE_TIME[city] < COOLDOWN:
            return False

    # Minimum Qualität
    if model < 50:
        return False

    edge = model - market

    if edge < EDGE_THRESHOLD:
        return False

    action = "BUY YES" if model > market else "BUY NO"

    trade = {
        "city": city,
        "model": model,
        "market": market,
        "edge": edge,
        "action": action,
        "amount": BET_AMOUNT,
        "time": datetime.utcnow()
    }

    portfolio["trades"].append(trade)
    LAST_TRADE_TIME[city] = now

    send_telegram(
        f"💰 PAPER TRADE\n"
        f"📍 {city}\n"
        f"🧠 Model: {model}%\n"
        f"📊 Market: {market}%\n"
        f"📈 Edge: {round(edge,2)}%\n"
        f"🎯 {action}\n"
        f"💵 {BET_AMOUNT}$"
    )

    resolve_trade(trade)

    return True

# ========================
# RESULT SIMULATION
# ========================
def resolve_trade(trade):
    outcome = (time.time() % 2) > 1

    if outcome:
        profit = trade["amount"] * 0.8
        portfolio["balance"] += profit
        portfolio["wins"] += 1
        result = "WIN ✅"
    else:
        portfolio["balance"] -= trade["amount"]
        portfolio["losses"] += 1
        result = "LOSS ❌"

    send_telegram(
        f"📊 RESULT\n"
        f"{result}\n"
        f"💰 Balance: {round(portfolio['balance'],2)}$\n"
        f"🏆 Wins: {portfolio['wins']} | ❌ Losses: {portfolio['losses']}"
    )

# ========================
# MAIN LOOP
# ========================
def run():
    send_telegram("🤖 Paper Trading (Optimized) gestartet")

    while True:
        print("Neue Analyse...")

        trades_count = 0

        for city in CITIES:
            if trades_count >= MAX_TRADES_PER_RUN:
                break

            try:
                weather = get_weather(city)

                if weather.get("cod") != 200:
                    print(f"API Error: {city}")
                    continue

                model = calculate_model(weather)
                market = get_market_probability()

                print(f"{city}: Model {model} | Market {market}")

                executed = place_paper_trade(city, model, market)

                if executed:
                    trades_count += 1

            except Exception as e:
                print("Error:", e)

        time.sleep(60)

# ========================
# START
# ========================
if __name__ == "__main__":
    run()
