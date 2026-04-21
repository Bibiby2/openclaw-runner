import time
import requests
import os

API_KEY = os.getenv("WEATHER_API_KEY")
CITY = "Vienna"

print("🌦️ Weather Bot läuft!")

def get_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    temp = data["main"]["temp"]
    weather = data["weather"][0]["main"]

    return temp, weather

while True:
    try:
        temp, weather = get_weather()
        print(f"🌡️ {CITY}: {temp}°C | {weather}")

        if temp > 25:
            print("🔥 Warm → Sommer Modus")
        elif temp < 10:
            print("❄️ Kalt → Winter Modus")
        else:
            print("🌤️ Normal")

    except Exception as e:
        print("❌ Fehler:", e)

    time.sleep(30)
