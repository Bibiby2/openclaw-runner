import requests
import os
import time

CITY = "Vienna"

API_KEY = os.getenv("WEATHER_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

        requests.post(url, data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        })

        print("Telegram gesendet:", message)

    except Exception as e:
        print("Telegram Fehler:", e)


def get_weather():
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()

        temp = data["main"]["temp"]
        weather = data["weather"][0]["main"]

        return temp, weather

    except Exception as e:
        print("Wetterfehler:", e)
        return None, None


print("Bot gestartet")

while True:
    try:
        temp, weather = get_weather()

        if temp is None:
            time.sleep(10)
            continue

        print(f"{CITY}: {temp}°C | {weather}")

        send_telegram(f"{CITY}: {temp}°C | {weather}")

        time.sleep(60)

    except Exception as e:
        print("Loop Fehler:", e)
        time.sleep(10)
