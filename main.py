import os
import time
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

EDGE_THRESHOLD = 8   # leicht reduziert für mehr Trades
STAKE = 2

# ---------------- TELEGRAM ----------------
def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg})

# ---------------- WEATHER MODEL ----------------
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    r = requests.get(url).json()

    rain = r.get("rain", {}).get("1h", 0)
    clouds = r["clouds"]["all"]
    humidity = r["main"]["humidity"]
    temp = r["main"]["temp"]

    # stärkeres Modell
    prob = (clouds * 0.3) + (humidity * 0.2) + (rain * 40)

    return min(prob, 100), temp

# ---------------- GET ALL MARKETS ----------------
def get_markets():
    url = "https://gamma-api.polymarket.com/markets"
    return requests.get(url).json()

# ---------------- FILTER WEATHER ----------------
def is_weather_market(title):
    keywords = ["temperature", "rain", "precipitation", "weather", "°c"]
    return any(k in title for k in keywords)

# ---------------- EXTRACT CITY ----------------
def extract_city(title):
    cities = ["new york", "london", "hong kong", "tokyo", "paris", "shanghai", "seoul"]

    for c in cities:
        if c in title:
            return c.title()

    return None

# ---------------- ANALYZE ----------------
def analyze_all():
    markets = get_markets()
    best_trade = None

    for m in markets:
        title = m.get("question", "").lower()

        if not is_weather_market(title):
            continue

        city = extract_city(title)
        if not city:
            continue

        try:
            market = float(m["outcomePrices"][0]) * 100
        except:
            continue

        model, temp = get_weather(city)

        edge = model - market

        print(f"{city} | Model {model:.1f} | Market {market:.1f} | Edge {edge:.1f}")

        if edge > EDGE_THRESHOLD:
            if not best_trade or edge > best_trade["edge"]:
                best_trade = {
                    "city": city,
                    "model": model,
                    "market": market,
                    "edge": edge,
                    "title": m["question"]
                }

    return best_trade

# ---------------- MAIN ----------------
send("🚀 B3 BOT (FULL MARKET SCAN) gestartet")

while True:
    print("\n--- Neue Analyse ---")

    trade = analyze_all()

    if trade:
        msg = f"""
💰 BEST TRADE
📍 {trade['city']}

📊 {trade['title']}

🧠 Model: {trade['model']:.1f}%
📊 Market: {trade['market']:.1f}%
📈 Edge: {trade['edge']:.1f}%

🎯 BUY YES
💵 ${STAKE}
"""
        send(msg)
    else:
        print("❌ Kein Trade gefunden")

    time.sleep(120)
