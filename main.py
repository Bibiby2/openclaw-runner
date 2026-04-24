import requests
import time
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_KEY = os.getenv("OPENWEATHER_API_KEY")

CITIES = {
    "New York": {"lat": 40.7128, "lon": -74.0060},
    "London": {"lat": 51.5074, "lon": -0.1278},
    "Hong Kong": {"lat": 22.3193, "lon": 114.1694}
}

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg})

def get_weather(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    
    try:
        res = requests.get(url)
        data = res.json()
        
        print("RAW API RESPONSE:", data)  # 🔥 WICHTIG
        
        return data
    except Exception as e:
        print("API Error:", e)
        return {}

def safe_get(data, path, default=0):
    try:
        for key in path:
            data = data[key]
        return data
    except:
        return default

def calculate_model(data):
    wind = safe_get(data, ["wind", "speed"], 0)
    humidity = safe_get(data, ["main", "humidity"], 0)
    clouds = safe_get(data, ["clouds", "all"], 0)
    rain = safe_get(data, ["rain", "1h"], 0)

    score = (rain * 15) + (clouds * 0.3) + (humidity * 0.2) - (wind * 2)
    return max(0, min(100, score))

def run():
    send_telegram("🔍 DEBUG MODE gestartet")

    while True:
        print("Neue Analyse...")

        for city, coord in CITIES.items():
            data = get_weather(coord["lat"], coord["lon"])

            if "main" not in data:
                print(f"❌ API Problem für {city}")
                continue

            model = calculate_model(data)
            print(f"{city} Model:", model)

        time.sleep(300)

run()
