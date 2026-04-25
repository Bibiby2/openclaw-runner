import requests
import time
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("OPENWEATHER_API_KEY")

# ========================
# SETTINGS
# ========================
CITIES = {
    "London": "https://polymarket.com/event/precipitation-in-london-in-april",
    "New York": "https://polymarket.com/event/precipitation-in-nyc-in-april",
    "Hong Kong": "https://polymarket.com/event/precipitation-in-hong-kong-in-april"
}

EDGE_THRESHOLD = 10

# ========================
# TELEGRAM
# ========================
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# ========================
# WEATHER
# ========================
def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    return requests.get(url).json()

# ========================
# MODEL
# ========================
def calculate_model(data):
    humidity = data["main"]["humidity"]
    clouds = data["clouds"]["all"]
    wind = data["wind"]["speed"]

    score = 0

    if humidity > 70:
        score += 30
    if clouds > 60:
        score += 30
    if wind > 5:
        score += 20

    return min(score, 90)

# ========================
# REAL MARKET (SCRAPE)
# ========================
def get_market_probability(url):
    try:
        html = requests.get(url).text

        import re
        match = re.search(r'(\d{1,2})\%', html)

        if match:
            return float(match.group(1))
        return None

    except:
        return None

# ========================
# MAIN
# ========================
def run():
    send_telegram("🚀 REAL DATA BOT gestartet")

    while True:
        print("\n--- Analyse ---")

        for city, url in CITIES.items():
            try:
                weather = get_weather(city)

                if weather.get("cod") != 200:
                    continue

                model = calculate_model(weather)
                market = get_market_probability(url)

                if market is None:
                    print(f"❌ Kein Market: {city}")
                    continue

                edge = model - market

                print(f"{city}: Model {model} | Market {market} | Edge {edge}")

                if edge > EDGE_THRESHOLD:
                    send_telegram(
                        f"💰 REAL EDGE\n"
                        f"{city}\n"
                        f"Model: {model}%\n"
                        f"Market: {market}%\n"
                        f"Edge: {round(edge,2)}%\n"
                        f"👉 BUY YES"
                    )
                else:
                    print("❌ Kein Value")

            except Exception as e:
                print("Error:", e)

        time.sleep(120)

run()
