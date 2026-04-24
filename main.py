import requests
import time
import os
from datetime import datetime

# ================================
# 🔑 ENV VARS
# ================================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# ================================
# ⚙️ SETTINGS (BALANCED MODE)
# ================================
CITIES = ["London", "New York", "Hong Kong"]

EDGE_THRESHOLD = 10      # weniger strikt → mehr Trades
MIN_MODEL = 45           # Mindestqualität
MAX_TRADES_PER_RUN = 3

TRADE_AMOUNT = 2         # $ Paper Trade

# ================================
# 💰 PAPER TRADING
# ================================
balance = 100
wins = 0
losses = 0

# ================================
# 📩 TELEGRAM
# ================================
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        print("Telegram Error")

# ================================
# 🌦️ WEATHER DATA
# ================================
def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    try:
        res = requests.get(url).json()

        if res.get("cod") != 200:
            print(f"❌ API Problem für {city}: {res}")
            return None

        return {
            "temp": res["main"]["temp"],
            "humidity": res["main"]["humidity"],
            "wind": res["wind"]["speed"],
            "clouds": res["clouds"]["all"]
        }
    except Exception as e:
        print("Weather Error:", e)
        return None

# ================================
# 🧠 MODEL (IMPROVED)
# ================================
def calculate_model(data):
    score = 0

    # 🌧️ Regen Wahrscheinlichkeit (simple proxy)
    if data["humidity"] > 70:
        score += 30
    if data["clouds"] > 60:
        score += 30
    if data["wind"] > 5:
        score += 10
    if data["temp"] < 15:
        score += 10

    return min(score, 100)

# ================================
# 📊 MARKET (SIMULATED)
# ================================
def get_market_odds():
    import random
    return random.uniform(30, 80)

# ================================
# 💎 VALUE CHECK
# ================================
def is_value_bet(model, market):
    edge = model - market

    if model < MIN_MODEL:
        return False, edge

    if model < market:
        return False, edge

    if edge < EDGE_THRESHOLD:
        return False, edge

    return True, edge

# ================================
# 💰 PAPER TRADE
# ================================
def execute_trade(city, model, market, edge):
    global balance, wins, losses

    # 🎯 Entscheidung
    action = "BUY YES"

    # 📊 Ergebnis simulieren
    import random
    win = random.random() < (model / 100)

    if win:
        balance += TRADE_AMOUNT
        wins += 1
        result = "WIN ✅"
    else:
        balance -= TRADE_AMOUNT
        losses += 1
        result = "LOSS ❌"

    # 📩 Telegram
    msg = f"""
💰 PAPER TRADE
📍 {city}

🧠 Model: {round(model,1)}%
📊 Market: {round(market,1)}%
📈 Edge: {round(edge,1)}%

🎯 {action}
💵 ${TRADE_AMOUNT}

📊 RESULT: {result}
💰 Balance: {round(balance,2)}$
🏆 Wins: {wins} ❌ Losses: {losses}
"""
    send_telegram(msg)

# ================================
# 🔁 MAIN LOOP
# ================================
def run_bot():
    print("🚀 VALUE BOT läuft...")

    while True:
        print("\n--- Neue Analyse ---")

        trades_done = 0

        for city in CITIES:
            if trades_done >= MAX_TRADES_PER_RUN:
                break

            data = get_weather(city)
            if not data:
                continue

            model = calculate_model(data)
            market = get_market_odds()

            valid, edge = is_value_bet(model, market)

            print(f"{city}: Model {model}% | Market {round(market,1)}% | Edge {round(edge,1)}%")

            if valid:
                execute_trade(city, model, market, edge)
                trades_done += 1
            else:
                print(f"❌ Kein Value: {city}")

        time.sleep(60)

# ================================
# ▶️ START
# ================================
if __name__ == "__main__":
    run_bot()
