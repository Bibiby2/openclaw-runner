import os
import time
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

EDGE_THRESHOLD = 10
STAKE = 2

CITIES = {
    "New York": "precipitation-in-nyc-in-april",
    "London": "precipitation-in-london-in-april",
    "Hong Kong": "precipitation-in-hong-kong-in-april"
}

# ---------------- TELEGRAM ----------------
def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg})

# ---------------- WEATHER MODEL ----------------
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    r = requests.get(url).json()

    rain = 0
    clouds = r["clouds"]["all"]
    humidity = r["main"]["humidity"]

    if "rain" in r:
        rain = r["rain"].get("1h", 0)

    # simple model
    prob = (clouds * 0.4) + (humidity * 0.3) + (rain * 30)

    return min(prob, 100)

# ---------------- POLYMARKET ----------------
def get_market(slug):
    try:
        url = f"https://gamma-api.polymarket.com/markets?slug={slug}"
        r = requests.get(url).json()

        if not r:
            return None

        market = r[0]

        # outcome prices
        yes_price = float(market["outcomePrices"][0])

        # convert to %
        return yes_price * 100

    except:
        return None

# ---------------- EDGE ----------------
def analyze(city, slug):
    model = get_weather(city)
    market = get_market(slug)

    if market is None:
        print(f"❌ Kein Market: {city}")
        return None

    edge = model - market

    print(f"{city}: Model {model:.1f}% | Market {market:.1f}% | Edge {edge:.1f}%")

    if edge > EDGE_THRESHOLD:
        return {
            "city": city,
            "model": model,
            "market": market,
            "edge": edge
        }

    return None

# ---------------- MAIN LOOP ----------------
send("🚀 REAL DATA BOT (B2) gestartet")

while True:
    print("\n--- Neue Analyse ---")

    for city, slug in CITIES.items():
        result = analyze(city, slug)

        if result:
            msg = f"""
💰 REAL TRADE
📍 {result['city']}

🧠 Model: {result['model']:.1f}%
📊 Market: {result['market']:.1f}%
📈 Edge: {result['edge']:.1f}%

🎯 BUY YES
💵 ${STAKE}
"""
            send(msg)

    time.sleep(120)
