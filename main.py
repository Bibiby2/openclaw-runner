 import requests
import os
import time

# =========================
# CONFIG
# =========================
CITY = "Vienna"
URL = "https://api.openweathermap.org/data/2.5/weather"

API_KEY = os.getenv("WEATHER_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# =========================
# TELEGRAM FUNCTION
# =========================
def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

        response = requests.post(url, data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        })

        print("📤 Telegram gesendet:", message)

    except Exception as e:
        print("❌ Telegram Fehler:", e)

# =========================
# WEATHER FUNCTION
# =========================
def get_weather():
    try:
        params = {
            "q": CITY,
            "appid": API_KEY,
            "units": "metric"
        }

        response = requests.get(URL, params=params)
        data = response.json()

        print("🌐 API Response:", data)

        temp = data["main"]["temp"]
        weather = data["weather"][0]["main"]

        return temp, weather

    except Exception as e:
        print("❌ Wetter Fehler:", e)
        return None, None

# =========================
# DECISION ENGINE
# =========================
def decide_action(temp, weather):

    if weather.lower() == "rain":
        return "RAIN"

    elif temp < 5:
        return "COLD"

    elif temp > 30:
        return "HOT"

    else:
        return "NORMAL"

# =========================
# MAIN LOOP
# =========================
print("🚀 Smart Weather Bot gestartet!")

while True:
    try:
        temp, weather = get_weather()

        if temp is None:
            time.sleep(10)
            continue

        action = decide_action(temp, weather)

        print(f"📊 {CITY}: {temp}°C | {weather} → {action}")

        # =========================
        # ACTIONS
        # =========================
        if action == "RAIN":
            send_telegram("🌧️ Regen! Perfekt für Indoor-Produkte 🛋️")

        elif action == "COLD":
            send_telegram("🥶 Kalt! Zeit für warme Kleidung 🧥")

        elif action == "HOT":
            send_telegram("🔥 Heiß! Sommer-Produkte verkaufen ☀️")

        elif action == "NORMAL":
            print("☁️ Kein Alert nötig")

        # =========================
        # TEST (WICHTIG!)
        # =========================
        send_telegram("🔥 TEST läuft – Bot aktiv!")

        # Warte 60 Sekunden
        time.sleep(60)

    except Exception as e:
        print("❌ Fehler im Loop:", e)
        time.sleep(10)
