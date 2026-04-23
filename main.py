import requests
import os
import time

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

CITIES = ["Vienna", "London", "New York", "Hong Kong"]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    try:
        requests.post(url, data=data)
        print("Telegram gesendet:", message)
    except Exception as e:
        print("Telegram Fehler:", e)

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    return requests.get(url).json()

def run():
    print("🚀 BOT STARTET...")

    # 🔥 TEST MESSAGE BEIM START
    send_telegram("✅ BOT IST ONLINE UND LÄUFT!")

    while True:
        print("\n--- Neue Runde ---")

        for city in CITIES:
            try:
                data = get_weather(city)

                temp = data["main"]["temp"]
                weather = data["weather"][0]["main"]

                print(f"{city}: {temp}°C | {weather}")

                # 🔥 IMMER TEST SIGNAL (damit du sicher was bekommst)
                send_telegram(f"🔥 TEST SIGNAL aus {city}: {temp}°C | {weather}")

            except Exception as e:
                print("Fehler:", e)

        time.sleep(60)  # jede Minute

if __name__ == "__main__":
    run()
