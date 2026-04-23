import requests
import os
import time
from datetime import datetime, timedelta

# ==============================
# ENV
# ==============================
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ==============================
# SETTINGS
# ==============================
CITIES = ["Vienna", "London", "New York", "Hong Kong"]

HOT_THRESHOLD = 30
COLD_THRESHOLD = 3
WIND_THRESHOLD = 12

COOLDOWN_MINUTES = 60
last_signal_time = {}

# ==============================
# TELEGRAM
# ==============================
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    try:
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print("Telegram Fehler:", e)

# ==============================
# WEATHER
# ==============================
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    return requests.get(url).json()

# ==============================
# SIGNAL LOGIK
# ==============================
def get_signal(city, data):
    temp = data["main"]["temp"]
    weather_main = data["weather"][0]["main"].lower()
    description = data["weather"][0]["description"].lower()
    wind = data["wind"]["speed"]

    # 🌧 Starkregen
    if "rain" in weather_main or "thunderstorm" in weather_main:
        if "heavy" in description or "thunderstorm" in description:
            return "RAIN_STRONG", f"{description}"

    # 🔥 Extreme Hitze
    if temp >= HOT_THRESHOLD:
        return "EXTREME_HEAT", f"{temp}°C"

    # ❄️ Extreme Kälte
    if temp <= COLD_THRESHOLD:
        return "EXTREME_COLD", f"{temp}°C"

    # 🌪 Starker Wind
    if wind >= WIND_THRESHOLD:
        return "HIGH_WIND", f"{wind} m/s"

    return None, None

# ==============================
# COOLDOWN
# ==============================
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

# ==============================
# MAIN LOOP
# ==============================
def run():
    print("🚀 STRONG BOT läuft...")
    send_telegram("✅ Bot ONLINE (Strong Mode aktiv)")

    while True:
        print("\n--- Analyse ---")

        for city in CITIES:
            try:
                data = get_weather(city)

                temp = data["main"]["temp"]
                weather = data["weather"][0]["description"]

                print(f"{city}: {temp}°C | {weather}")

                signal, reason = get_signal(city, data)

                if signal:
                    if can_send(city, signal):
                        msg = f"""
🚨 SIGNAL 🚨

📍 {city}
🌡 {temp}°C
☁️ {weather}

📊 {signal}
🧠 {reason}

👉 Trade prüfen!
"""
                        send_telegram(msg)
                        print(f"✅ SIGNAL gesendet: {city}")
                    else:
                        print(f"⏳ Cooldown: {city}")

                else:
                    print(f"— Kein Signal für {city}")

            except Exception as e:
                print("Fehler:", e)

        time.sleep(300)

if __name__ == "__main__":
    run()
