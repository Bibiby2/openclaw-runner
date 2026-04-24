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
EDGE_THRESHOLD = 5  # nur Trades >5% Edge

# ========================
# STORAGE (Paper Trading)
# ========================
portfolio = {
    "balance": 100.0,
    "trades": [],
    "wins": 0,
    "losses": 0
}

# ========================
# TELEGRAM
# ========================
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# ========================
# WEATHER
# ========================
def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    r = requests.get(url)
    return r.json()

# ========================
# MODEL (simple)
# ========================
def calculate_model(weather):
    rain = weather.get("rain", {}).get("1h", 0)
    clouds = weather["clouds"]["all"]
    humidity = weather["main"]["humidity"]

    score = 0

    if rain > 0:
        score += 40
    if clouds > 70:
        score += 30
    if humidity > 70:
        score += 30

    return min(score, 100)

# ========================
# MARKET SIMULATION
# ========================
def get_market_probability():
    return round(30 + (70 * (time.time() % 1)), 2)  # fake dynamic %

# ========================
# PAPER TRADE
# ========================
def place_paper_trade(city, model, market):

    edge = model - market

    if edge < EDGE_THRESHOLD:
        print(f"❌ No Value: {city}")
        return

    # Entscheidung
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

# ========================
# RESULT SIMULATION
# ========================
def resolve_trade(trade):
    # Fake Ergebnis (random)
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
    send_telegram("🤖 Paper Trading gestartet")

    while True:
        print("Neue Analyse...")

        for city in CITIES:
            try:
                weather = get_weather(city)
                model = calculate_model(weather)
                market = get_market_probability()

                print(f"{city}: Model {model} | Market {market}")

                place_paper_trade(city, model, market)

            except Exception as e:
                print("Error:", e)

        time.sleep(60)

if __name__ == "__main__":
    run()
