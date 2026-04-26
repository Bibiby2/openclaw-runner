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
# 🌍 SETTINGS (BALANCED MODE)
# ==============================
CITIES = ["New York", "London", "Hong Kong"]

MIN_EDGE = 15
MIN_MODEL = 50
MIN_MARKET = 30
MAX_MARKET = 70

TRADE_COOLDOWN_MINUTES = 20

BASE_BET = 2
BOOST_BET = 3

last_trade_time = {}

# ==============================
# 📩 TELEGRAM
# ==============================
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg})
    except:
        print("Telegram Fehler")

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
        print(f"⚠️ Request Fehler: {city}")
        return None

# ==============================
# 🧠 MODEL
# ==============================
def calculate_model(weather):
    rain = weather.get("rain", {}).get("1h", 0)
    clouds = weather["clouds"]["all"]
    humidity = weather["main"]["humidity"]

    score = 0

    if rain > 0:
        score += 40
    if clouds > 50:
        score += 20
    if humidity > 65:
        score += 20

    return min(score, 100)

# ==============================
# 📊 MARKET SIMULATION
# ==============================
def get_market_prob():
    import random
    return random.uniform(30, 70)

# ==============================
# 📈 EDGE
# ==============================
def calculate_edge(model, market):
    return model - market

# ==============================
# ⏱️ COOLDOWN
# ==============================
def can_trade(city):
    if city not in last_trade_time:
        return True
    return datetime.now() - last_trade_time[city] > timedelta(minutes=TRADE_COOLDOWN_MINUTES)

# ==============================
# 💰 TRADE ENGINE
# ==============================
def process_city(city):
    weather = get_weather(city)
    if not weather:
        return False

    model = calculate_model(weather)
    market = get_market_prob()
    edge = calculate_edge(model, market)

    print(f"{city}: Model {model:.1f} | Market {market:.1f} | Edge {edge:.1f}")

    # FILTERS
    if model < MIN_MODEL:
        return False
    if market < MIN_MARKET or market > MAX_MARKET:
        return False
    if edge < MIN_EDGE:
        return False
    if not can_trade(city):
        return False

    # BET SIZE
    bet = BOOST_BET if edge >= 30 else BASE_BET

    last_trade_time[city] = datetime.now()

    msg = f"""
💰 REAL EDGE (BALANCED)
📍 {city}

🧠 Model: {model:.1f}%
📊 Market: {market:.1f}%
📈 Edge: {edge:.1f}%

🎯 BUY YES
💵 ${bet}
"""
    send_telegram(msg)

    return True

# ==============================
# 🔁 MAIN LOOP
# ==============================
def run_bot():
    send_telegram("🚀 REAL DATA BOT (BALANCED MODE) gestartet")

    while True:
        print("\n--- Neue Analyse ---")

        trade_found = False

        for city in CITIES:
            if process_city(city):
                trade_found = True

        if not trade_found:
            print("⚠️ Kein Trade gefunden")

        time.sleep(60)

# ==============================
# ▶️ START
# ==============================
if __name__ == "__main__":
    run_bot()
