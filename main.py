import requests
import os
import time
from datetime import datetime, timedelta

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

CITIES = ["Vienna", "London", "New York", "Hong Kong"]

COOLDOWN_MINUTES = 60
last_signal_time = {}

POLYMARKET_LINKS = {
    "London": "https://polymarket.com/event/precipitation-in-london-in-april",
    "New York": "https://polymarket.com/event/precipitation-in-nyc-in-april",
    "Hong Kong": "https://polymarket.com/event/precipitation-in-hong-kong-in-april"
}

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg
    })

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    return requests.get(url).json()

def smart_decision(data):
    wind = data["wind"]["speed"]
    clouds = data["clouds"]["all"]
    humidity = data["main"]["humidity"]

    score = 0

    # Wind Bewertung
    if wind >= 18:
        score += 4
    elif wind >= 14:
        score += 2

    # Clouds Bewertung
    if clouds >= 80:
        score += 3
    elif clouds >= 50:
        score += 1

    # Humidity Bewertung
    if humidity >= 80:
        score += 3
    elif humidity >= 60:
        score += 1

    # Entscheidung
    if score >= 7:
        return "BUY_YES", score
    elif score <= 2:
        return "BUY_NO", score
    else:
        return "SKIP", score

def can_send(city, action):
    key = (city, action)
    now = datetime.utcnow()

    if key not in last_signal_time:
        last_signal_time[key] = now
        return True

    if now - last_signal_time[key] > timedelta(minutes=COOLDOWN_MINUTES):
        last_signal_time[key] = now
        return True

    return False

def run():
    print("🚀 SMART BOT läuft...")
    send_telegram("🧠 Smart Trading Bot ONLINE")

    while True:
        print("\n--- Analyse ---")

        for city in CITIES:
            try:
                data = get_weather(city)

                temp = data["main"]["temp"]
                weather = data["weather"][0]["description"]
                wind = data["wind"]["speed"]
                clouds = data["clouds"]["all"]
                humidity = data["main"]["humidity"]

                action, score = smart_decision(data)

                if action == "SKIP":
                    print(f"⚠️ Skip: {city} (Score {score})")
                    continue

                if can_send(city, action):

                    link = POLYMARKET_LINKS.get(city, "https://polymarket.com")

                    msg = f"""
🚨 SMART TRADE 🚨

📍 {city}
🌡 {temp}°C
☁️ {weather}

🌪 Wind: {wind} m/s
☁️ Clouds: {clouds}%
💧 Humidity: {humidity}%

🧠 Score: {score}/10

🎯 ACTION: {action.replace("_", " ")}

🔗 {link}

💰 Einsatz: max $2
"""

                    send_telegram(msg)
                    print(f"✅ {action} → {city} (Score {score})")

                else:
                    print(f"— Cooldown: {city}")

            except Exception as e:
                print("Fehler:", e)

        time.sleep(300)

if __name__ == "__main__":
    run()
