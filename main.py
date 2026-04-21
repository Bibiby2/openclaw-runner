import time
import requests
import os

API_KEY = os.getenv("WEATHER_API_KEY")
CITY = "Vienna"

print("🌦️ Smart Weather Bot läuft!")

# -----------------------------
# WEATHER FUNCTION
# -----------------------------
def get_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    print("API Response:", data)

    if "main" not in data:
        raise Exception(data)

    temp = data["main"]["temp"]
    weather = data["weather"][0]["main"]

    return temp, weather

# -----------------------------
# DECISION ENGINE
# -----------------------------
def decision_engine(temp, weather):
    if "Rain" in weather:
        return "RAIN_ALERT"
    elif temp > 28:
        return "HEAT_ALERT"
    elif temp < 5:
        return "COLD_ALERT"
    else:
        return "NORMAL"

# -----------------------------
# TELEGRAM FUNCTION
# -----------------------------
def send_telegram(message):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("❌ Telegram nicht konfiguriert")
        return

    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        response = requests.post(url, json={
            "chat_id": chat_id,
            "text": message
        })

        print("📩 Telegram gesendet:", response.text)

    except Exception as e:
        print("❌ Telegram Fehler:", e)

# -----------------------------
# MAIN LOOP
# -----------------------------
while True:
    try:
        temp, weather = get_weather()
        action = decision_engine(temp, weather)

        print(f"🌡️ {CITY}: {temp}°C | {weather} → {action}")

        # 🔥 ACTION TRIGGERS
        if action == "RAIN_ALERT":
            send_telegram("🌧️ Es regnet! Perfekt für Indoor-Produkte ☕📚")

        elif action == "HEAT_ALERT":
            send_telegram("🔥 Heiß! Sommer-Produkte verkaufen 🧃")

        elif action == "COLD_ALERT":
            send_telegram("❄️ Kalt! Winter-Produkte 🧥")

    except Exception as e:
        print("❌ Fehler:", e)

    time.sleep(30)
