import requests
import time
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

API_KEY = "YOUR_OPENWEATHER_API_KEY"

CITIES = {
    "New York": {"lat": 40.7128, "lon": -74.0060},
    "London": {"lat": 51.5074, "lon": -0.1278},
    "Hong Kong": {"lat": 22.3193, "lon": 114.1694}
}

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": msg})
    except:
        print("Telegram Error")

def get_weather(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    try:
        res = requests.get(url).json()
        return res
    except:
        return {}

def safe_get(data, path, default=0):
    """Safe dictionary access"""
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

    score = 0

    # 🌧️ Rain weight
    score += rain * 15

    # ☁️ Clouds
    score += clouds * 0.3

    # 💧 Humidity
    score += humidity * 0.2

    # 🌬️ Wind reduces rain probability
    score -= wind * 2

    score = max(0, min(100, score))
    return score

def fake_market():
    return round(40 + (time.time() % 20), 2)

def run():
    send_telegram("🚀 FINAL BOT gestartet (SAFE MODE)")

    while True:
        print("Neue Analyse...")

        for city, coord in CITIES.items():
            data = get_weather(coord["lat"], coord["lon"])

            if not data or "main" not in data:
                print(f"⚠️ Keine gültigen Daten für {city}")
                continue

            try:
                model = calculate_model(data)
                market = fake_market()
                edge = model - market

                print(city, model, market, edge)

                if edge > 5:
                    action = "BUY YES"
                elif edge < -5:
                    action = "BUY NO"
                else:
                    continue

                msg = f"""
💰 VALUE TRADE

📍 {city}
🧠 Model: {model:.2f}%
📊 Market: {market:.2f}%
📈 Edge: {edge:.2f}%

🎯 ACTION: {action}
💵 Einsatz: $2
"""
                send_telegram(msg)

            except Exception as e:
                print("Error:", e)

        time.sleep(300)

run()
