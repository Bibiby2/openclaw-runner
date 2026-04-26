import os
import time
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("OPENWEATHER_API_KEY")

CITIES = ["New York", "London", "Hong Kong"]

# STATE
last_trade_time = {}
blocked_cities = {}

# ⚙️ BALANCED SETTINGS
COOLDOWN_SECONDS = 180  # 3 Minuten (vorher 5)
EDGE_THRESHOLD = 8
MIN_MODEL = 40

def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg})

def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    r = requests.get(url).json()
    if r.get("cod") != 200:
        return None
    return r

def rain_model(w):
    rain = w.get("rain", {}).get("1h", 0)
    clouds = w["clouds"]["all"]
    humidity = w["main"]["humidity"]

    score = 0

    if rain > 0:
        score += 50
    if rain > 2:
        score += 20
    if clouds > 60:
        score += 20
    if humidity > 70:
        score += 10

    return min(score, 100)

def market_score():
    return 45 + (time.time() % 15)

def can_trade(city):
    now = time.time()

    if city in last_trade_time:
        if now - last_trade_time[city] < COOLDOWN_SECONDS:
            return False, "Cooldown"

    if city in blocked_cities:
        return False, "Blocked"

    return True, "OK"

def run():
    send("⚖️ BALANCED SAFE MODE gestartet")

    while True:
        print("\n--- Analyse ---")

        for city in CITIES:
            allowed, reason = can_trade(city)

            if not allowed:
                print(f"⛔ {city}: {reason}")
                continue

            w = get_weather(city)

            if not w:
                print(f"❌ Kein Data: {city}")
                continue

            model = rain_model(w)
            market = market_score()
            edge = model - market

            print(f"{city}: Model {model} | Market {market} | Edge {edge}")

            # FILTER
            if model < MIN_MODEL:
                print("⚠️ Model zu schwach")
                continue

            if edge < EDGE_THRESHOLD:
                print("⚠️ Edge zu klein")
                continue

            if market > 70:
                print("⚠️ Market zu hoch")
                continue

            # TRADE
            msg = f"""⚖️ BALANCED TRADE
📍 {city}

🧠 Model: {model:.1f}%
📊 Market: {market:.1f}%
📈 Edge: {edge:.1f}%

🎯 BUY YES
💵 $2
"""
            send(msg)

            last_trade_time[city] = time.time()

        time.sleep(60)

if __name__ == "__main__":
    run()
