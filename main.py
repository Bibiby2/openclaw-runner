import requests
import os
import time
from datetime import datetime, timedelta

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

CITIES = ["Vienna", "London", "New York", "Hong Kong"]

COOLDOWN_MINUTES = 60
last_signal_time = {}

POLYMARKET_LINKS = {
    "London": "https://polymarket.com/event/precipitation-in-london-in-april",
    "New York": "https://polymarket.com/event/precipitation-in-nyc-in-april",
    "Hong Kong": "https://polymarket.com/event/precipitation-in-hong-kong-in-april"
}

# 👉 Simulierte Marktpreise (später echte API)
MARKET_PROB = {
    "London": 0.75,
    "New York": 0.65,
    "Hong Kong": 0.55
}

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg
    })

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    return requests.get(url).json()

def calculate_probability(data):
    wind = data["wind"]["speed"]
    clouds = data["clouds"]["all"]
    humidity = data["main"]["humidity"]

    score = 0

    if wind >= 18:
        score += 4
    elif wind >= 14:
        score += 2

    if clouds >= 80:
        score += 3
    elif clouds >= 50:
        score += 1

    if humidity >= 80:
        score += 3
    elif humidity >= 60:
        score += 1

    # 👉 convert score → probability
    prob = score / 10
    return prob, score

def value_decision(city, model_prob):
    market_prob = MARKET_PROB.get(city, 0.5)

    edge = model_prob - market_prob

    if edge > 0.15:
        return "BUY_YES", edge, market_prob
    elif edge < -0.15:
        return "BUY_NO", edge, market_prob
    else:
        return "SKIP", edge, market_prob

def can_send(city):
    now = datetime.utcnow()

    if city not in last_signal_time:
        last_signal_time[city] = now
        return True

    if now - last_signal_time[city] > timedelta(minutes=COOLDOWN_MINUTES):
        last_signal_time[city] = now
        return True

    return False

def run():
    print("🚀 VALUE BOT läuft...")
    send_telegram("💰 Value Trading Bot ONLINE")

    while True:
        print("\n--- Analyse ---")

        for city in CITIES:
            try:
                data = get_weather(city)

                temp = data["main"]["temp"]
                weather = data["weather"][0]["description"]

                model_prob, score = calculate_probability(data)
                action, edge, market_prob = value_decision(city, model_prob)

                if action == "SKIP":
                    print(f"❌ No Edge: {city}")
                    continue

                if can_send(city):

                    link = POLYMARKET_LINKS.get(city, "https://polymarket.com")

                    msg = f"""
💰 VALUE TRADE 💰

📍 {city}
🌡 {temp}°C
☁️ {weather}

🧠 Model: {round(model_prob*100)}%
📊 Market: {round(market_prob*100)}%
📈 Edge: {round(edge*100)}%

🎯 ACTION: {action.replace("_", " ")}

🔗 {link}

💵 Einsatz: max $2
"""

                    send_telegram(msg)
                    print(f"✅ VALUE TRADE: {city}")

                else:
                    print(f"— Cooldown: {city}")

            except Exception as e:
                print("Fehler:", e)

        time.sleep(300)

if __name__ == "__main__":
    run()
