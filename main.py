import requests
import time
import os
from datetime import datetime, timedelta

# ==============================
# 🔑 ENV VARIABLES
# ==============================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# ==============================
# 🌍 SETTINGS
# ==============================
CITIES = ["New York", "London", "Hong Kong"]

MIN_EDGE = 20
MIN_MODEL = 55
MIN_MARKET = 35
MAX_MARKET = 65

TRADE_COOLDOWN_MINUTES = 30

BASE_BET = 2
BOOST_BET = 3

last_trade_time = {}

# ==============================
# 📩 TELEGRAM
# ==============================
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg})

# ==============================
# 🌦️ WEATHER DATA
# ==============================
def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    try:
        res = requests.get(url).json()
        if res.get("cod") != 200:
            print(f"❌ API Problem: {city}", res)
            return None
        return res
    except:
        return None

# ==============================
# 🧠 MODEL (SIMPLE LOGIC)
# ==============================
def calculate_model(weather):
    rain = weather.get("rain", {}).get("1h", 0)
    clouds = weather["clouds"]["all"]
    humidity = weather["main"]["humidity"]

    score = 0

    if rain > 0:
        score += 40
    if clouds > 60:
        score += 20
    if humidity > 70:
        score += 20

    return min(score, 100)

# ==============================
# 📊 FAKE MARKET (SIMULATION)
# ==============================
def get_market_prob():
    import random
    return random.uniform(30, 70)

# ==============================
# 📈 EDGE CALC
# ==============================
def calculate_edge(model, market):
    return model - market

# ==============================
# ⏱️ COOLDOWN CHECK
# ==============================
def can_trade(city):
    if city not in last_trade_time:
        return True

    return datetime.now() - last_trade_time[city] > timedelta(minutes=TRADE_COOLDOWN_MINUTES)

# ==============================
# 💰 TRADE DECISION
# ==============================
def process_city(city):
    weather = get_weather(city)
    if not weather:
        print(f"⚠️ Keine Daten: {city}")
        return

    model = calculate_model(weather)
    market = get_market_prob()
    edge = calculate_edge(model, market)

    print(f"{city}: Model {model:.1f} | Market {market:.1f} | Edge {edge:.1f}")

    # 🔒 FILTERS
    if model < MIN_MODEL:
        return
    if market < MIN_MARKET or market > MAX_MARKET:
        return
    if edge < MIN_EDGE:
        return
    if not can_trade(city):
        return

    # 💵 BET SIZE
    bet = BOOST_BET if edge >= 30 else BASE_BET

    last_trade_time[city] = datetime.now()

    msg = f"""
💰 REAL EDGE
📍 {city}

🧠 Model: {model:.1f}%
📊 Market: {market:.1f}%
📈 Edge: {edge:.1f}%

🎯 BUY YES
💵 ${bet}
"""
    send_telegram(msg)

# ==============================
# 🔁 MAIN LOOP
# ==============================
def run_bot():
    send_telegram("🚀 REAL DATA BOT (FINAL OPTIMIZED) gestartet")

    while True:
        print("\n--- Neue Analyse ---")

        trade_found = False

        for city in CITIES:
            before = len(last_trade_time)
            process_city(city)
            after = len(last_trade_time)

            if after > before:
                trade_found = True

        if not trade_found:
            print("⚠️ Kein Trade gefunden")

        time.sleep(60)

# ==============================
# ▶️ START
# ==============================
if __name__ == "__main__":
    run_bot()
