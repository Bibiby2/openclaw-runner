import os
import time
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

EDGE_THRESHOLD = 10
STAKE = 2

CITIES = ["New York", "London", "Hong Kong"]

RAIN_KEYWORDS = ["rain", "precipitation", "shower", "rainfall"]

# ---------------- TELEGRAM ----------------
def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg})

# ---------------- WEATHER ----------------
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    r = requests.get(url).json()

    rain = r.get("rain", {}).get("1h", 0)
    clouds = r["clouds"]["all"]
    humidity = r["main"]["humidity"]

    prob = (clouds * 0.4) + (humidity * 0.3) + (rain * 30)
    return min(prob, 100)

# ---------------- MARKET SEARCH ----------------
def find_market(city):
    try:
        url = "https://gamma-api.polymarket.com/markets"
        markets = requests.get(url).json()

        for m in markets:
            title = m.get("question", "").lower()

            if city.lower() in title:
                if any(word in title for word in RAIN_KEYWORDS):
                    yes_price = float(m["outcomePrices"][0])
                    return yes_price * 100

        return None

    except Exception as e:
        print("Market Error:", e)
        return None

# ---------------- ANALYSE ----------------
def analyze(city):
    model = get_weather(city)
    market = find_market(city)

    if market is None:
        print(f"⚠️ Kein passender Market: {city}")
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

# ---------------- MAIN ----------------
send("🚀 REAL DATA BOT (B2 FINAL) gestartet")

while True:
    print("\n--- Neue Analyse ---")

    for city in CITIES:
        result = analyze(city)

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
