import requests
import time
import os

# ENV VARS
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Städte + Beispiel Market Preise (manuell ersetzt du später)
markets = [
    {"city": "New York", "lat": 40.7128, "lon": -74.0060, "yes_price": 0.65, "type": "low_rain"},
    {"city": "London", "lat": 51.5072, "lon": -0.1276, "yes_price": 0.90, "type": "low_rain"},
    {"city": "Hong Kong", "lat": 22.3193, "lon": 114.1694, "yes_price": 0.30, "type": "low_rain"}
]

def get_weather(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    return response.json()

def estimate_rain(data):
    # einfacher Proxy: Regen heute + morgen
    rain = 0
    daily = data.get("daily", [])
    for day in daily[:2]:
        rain += day.get("rain", 0)
    return rain

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg
    }
    requests.post(url, json=payload)

def analyze_market(city, rain, yes_price):
    # einfache Edge Logik
    if rain > 5 and yes_price > 0.6:
        return "🔥 BUY NO", "High"
    elif rain < 2 and yes_price < 0.5:
        return "🔥 BUY YES", "Medium"
    else:
        return "⚠️ SKIP", "Low"

def run_bot():
    print("🚀 Phase 2 Bot läuft...")

    for m in markets:
        try:
            data = get_weather(m["lat"], m["lon"])
            rain = estimate_rain(data)

            decision, strength = analyze_market(m["city"], rain, m["yes_price"])

            msg = f"""
📊 MARKET ANALYSIS

City: {m['city']}
Rain Estimate: {rain} mm
Market YES Price: {m['yes_price']}

Decision: {decision}
Confidence: {strength}
"""

            print(msg)
            send_telegram(msg)

        except Exception as e:
            print(f"❌ Fehler bei {m['city']}: {e}")

while True:
    run_bot()
    time.sleep(600)  # alle 10 Minuten
