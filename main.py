import os
import time
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("OPENWEATHER_API_KEY")

CITIES = ["New York", "London", "Hong Kong"]

def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg})

def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    r = requests.get(url).json()
    if r.get("cod") != 200:
        return None
    return r

# 🌧️ REGEN MODELL
def rain_model(w):
    rain = w.get("rain", {}).get("1h", 0)
    clouds = w["clouds"]["all"]
    humidity = w["main"]["humidity"]
    wind = w["wind"]["speed"]

    score = 0

    if rain > 0:
        score += 50
    if rain > 2:
        score += 20

    if clouds > 60:
        score += 20
    if clouds > 80:
        score += 10

    if humidity > 70:
        score += 15

    if wind > 5:
        score += 10

    return min(score, 100)

# ☀️ SONNE MODELL (NEU!)
def sun_model(w):
    clouds = w["clouds"]["all"]
    humidity = w["main"]["humidity"]
    temp = w["main"]["temp"]

    score = 0

    if clouds < 30:
        score += 40
    if clouds < 15:
        score += 20

    if humidity < 60:
        score += 20

    if temp > 20:
        score += 20
    if temp > 25:
        score += 20

    return min(score, 100)

# 📊 MARKET SIMULATION (placeholder)
def market_score():
    return 40 + (time.time() % 20)  # einfache Simulation

def run():
    send("🚀 WEATHER BOT (RAIN + SUN MODE) gestartet")

    while True:
        print("\n--- Neue Analyse ---")

        for city in CITIES:
            w = get_weather(city)

            if not w:
                print(f"❌ Kein Data: {city}")
                continue

            rain = rain_model(w)
            sun = sun_model(w)
            market = market_score()

            print(f"{city}: Rain {rain} | Sun {sun} | Market {market}")

            # 🌧️ RAIN TRADE
            edge_rain = rain - market

            if rain > 55 and edge_rain > 10:
                msg = f"""🌧️ RAIN EDGE
📍 {city}

🧠 Model: {rain:.1f}%
📊 Market: {market:.1f}%
📈 Edge: {edge_rain:.1f}%

🎯 BUY YES (RAIN)
💵 $2
"""
                send(msg)
                continue

            # ☀️ SUN TRADE
            edge_sun = sun - market

            if sun > 60 and edge_sun > 10:
                msg = f"""☀️ SUN EDGE
📍 {city}

🧠 Model: {sun:.1f}%
📊 Market: {market:.1f}%
📈 Edge: {edge_sun:.1f}%

🎯 BUY YES (SUN)
💵 $2
"""
                send(msg)
                continue

            print("⚠️ Kein Trade")

        time.sleep(60)

if __name__ == "__main__":
    run()
