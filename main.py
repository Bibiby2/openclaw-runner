import requests
import os
import time
from datetime import datetime, timedelta

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

CITIES = ["Vienna", "London", "New York", "Hong Kong"]

HIGH_WIND = 18
MID_WIND = 14

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

def decision(wind):
    if wind >= HIGH_WIND:
        return "BUY_YES", 9
    elif wind >= MID_WIND:
        return "SKIP", 6
    else:
        return "BUY_NO", 8

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
    print("🚀 AUTO BOT läuft...")
    send_telegram("🤖 Bot ONLINE (Trading Decision aktiv)")

    while True:
        print("\n--- Analyse ---")

        for city in CITIES:
            try:
                data = get_weather(city)

                temp = data["main"]["temp"]
                weather = data["weather"][0]["description"]
                wind = data["wind"]["speed"]

                action, score = decision(wind)

                if action == "SKIP":
                    print(f"⚠️ Skip: {city}")
                    continue

                if can_send(city, action):

                    link = POLYMARKET_LINKS.get(city, "https://polymarket.com")

                    action_text = "BUY YES" if action == "BUY_YES" else "BUY NO"

                    msg = f"""
🚨 TRADE SIGNAL 🚨

📍 {city}
🌡 {temp}°C
☁️ {weather}

🌪 Wind: {wind} m/s
🧠 Confidence: {score}/10

🎯 ACTION: {action_text}

🔗 {link}

💰 Einsatz: max $2
"""

                    send_telegram(msg)
                    print(f"✅ {action_text} → {city}")

                else:
                    print(f"— Cooldown: {city}")

            except Exception as e:
                print("Fehler:", e)

        time.sleep(300)

if __name__ == "__main__":
    run()
