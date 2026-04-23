import requests
import os
import time
from datetime import datetime, timedelta

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

CITIES = ["Vienna", "London", "New York", "Hong Kong"]

WIND_THRESHOLD = 14
STRONG_WIND = 18

COOLDOWN_MINUTES = 60
last_signal_time = {}

POLYMARKET_LINKS = {
    "London": "https://polymarket.com/event/precipitation-in-london-in-april",
    "New York": "https://polymarket.com/event/precipitation-in-nyc-in-april",
    "Hong Kong": "https://polymarket.com/event/precipitation-in-hong-kong-in-april"
}

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    })

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    return requests.get(url).json()

def confidence_score(wind):
    if wind >= 20:
        return 9
    elif wind >= 18:
        return 8
    elif wind >= 16:
        return 7
    elif wind >= 14:
        return 6
    return 0

def get_signal(data):
    wind = data["wind"]["speed"]
    if wind >= WIND_THRESHOLD:
        return "HIGH_WIND", wind
    return None, None

def can_send(city, signal):
    key = (city, signal)
    now = datetime.utcnow()

    if key not in last_signal_time:
        last_signal_time[key] = now
        return True

    if now - last_signal_time[key] >= timedelta(minutes=COOLDOWN_MINUTES):
        last_signal_time[key] = now
        return True

    return False

def run():
    print("🚀 AUTO BOT läuft...")
    send_telegram("✅ Bot ONLINE (Auto Trading vorbereitet)")

    while True:
        print("\n--- Analyse ---")

        for city in CITIES:
            try:
                data = get_weather(city)

                temp = data["main"]["temp"]
                weather = data["weather"][0]["description"]
                wind = data["wind"]["speed"]

                print(f"{city}: {temp}°C | Wind {wind}")

                signal, wind_val = get_signal(data)

                if signal and can_send(city, signal):

                    score = confidence_score(wind_val)

                    # ❌ Skip schlechte Trades
                    if score < 7:
                        print(f"❌ Skip Low Confidence: {city}")
                        continue

                    strength = "HIGH" if wind_val >= STRONG_WIND else "MEDIUM"

                    link = POLYMARKET_LINKS.get(city, "https://polymarket.com/")

                    msg = f"""
🚨 TRADE ALERT 🚨

📍 {city}
🌡 {temp}°C
☁️ {weather}

🌪 Wind: {wind_val} m/s
📊 Strength: {strength}
🧠 Confidence: {score}/10

💡 ACTION: BUY YES

🔗 {link}

⚠️ Einsatz: max $2
"""

                    send_telegram(msg)
                    print(f"✅ TRADE: {city}")

                else:
                    print(f"— Kein Signal: {city}")

            except Exception as e:
                print("Fehler:", e)

        time.sleep(300)

if __name__ == "__main__":
    run()
