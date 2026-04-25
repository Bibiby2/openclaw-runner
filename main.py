import requests
import time
import os
import random

# ================================
# 🔑 ENV VARS
# ================================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("OPENWEATHER_API_KEY")

# ================================
# ⚙️ SETTINGS
# ================================
CITIES = ["London", "New York", "Hong Kong"]

EDGE_THRESHOLD = 10   # realistischer
MIN_MODEL = 45        # Mindestqualität

# ================================
# 📩 TELEGRAM
# ================================
def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        print("Telegram Error")

# ================================
# 🌦️ WEATHER
# ================================
def get_weather(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        res = requests.get(url).json()

        if res.get("cod") != 200:
            print(f"❌ API Problem für {city}")
            return None

        return res
    except Exception as e:
        print("Weather Error:", e)
        return None

# ================================
# 🧠 MODEL
# ================================
def calculate_model(data):
    humidity = data["main"]["humidity"]
    clouds = data["clouds"]["all"]
    wind = data["wind"]["speed"]
    temp = data["main"]["temp"]

    score = 0

    if humidity > 70:
        score += 30
    if clouds > 60:
        score += 30
    if wind > 5:
        score += 10
    if temp < 15:
        score += 10

    return min(score, 90)

# ================================
# 📊 MARKET (STABILER PROXY)
# ================================
def get_market_probability(city):
    base_market = {
        "London": 45,
        "New York": 50,
        "Hong Kong": 55
    }

    noise = random.uniform(-5, 5)
    return round(base_market[city] + noise, 1)

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
# 🔁 MAIN LOOP
# ================================
def run_bot():
    send_telegram("🚀 REAL DATA BOT (STABLE MODE) gestartet")
    print("Bot läuft...")

    while True:
        print("\n--- Neue Analyse ---")

        for city in CITIES:
            try:
                weather = get_weather(city)
                if not weather:
                    continue

                model = calculate_model(weather)
                market = get_market_probability(city)

                valid, edge = is_value_bet(model, market)

                print(f"{city}: Model {model}% | Market {market}% | Edge {round(edge,1)}%")

                if valid:
                    send_telegram(
                        f"💰 REAL EDGE\n"
                        f"📍 {city}\n\n"
                        f"🧠 Model: {model}%\n"
                        f"📊 Market: {market}%\n"
                        f"📈 Edge: {round(edge,1)}%\n\n"
                        f"🎯 BUY YES"
                    )
                else:
                    print(f"❌ Kein Value: {city}")

            except Exception as e:
                print("Error:", e)

        time.sleep(120)

# ================================
# ▶️ START
# ================================
if __name__ == "__main__":
    run_bot()
