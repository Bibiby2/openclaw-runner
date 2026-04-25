import os
import time
import requests
import json
import random

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

EDGE_THRESHOLD = 8
STAKE = 2

DATA_FILE = "trades.json"

# ---------------- TELEGRAM ----------------
def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg})

# ---------------- LOAD/SAVE ----------------
def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {"balance": 100, "wins": 0, "losses": 0}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

data = load_data()

# ---------------- WEATHER ----------------
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    r = requests.get(url).json()

    rain = r.get("rain", {}).get("1h", 0)
    clouds = r["clouds"]["all"]
    humidity = r["main"]["humidity"]

    prob = (clouds * 0.3) + (humidity * 0.2) + (rain * 40)
    return min(prob, 100)

# ---------------- MARKETS ----------------
def get_markets():
    url = "https://gamma-api.polymarket.com/markets"
    return requests.get(url).json()

def is_weather_market(title):
    keywords = ["temperature", "rain", "precipitation", "weather"]
    return any(k in title for k in keywords)

def extract_city(title):
    cities = ["new york", "london", "hong kong", "tokyo", "paris"]
    for c in cities:
        if c in title:
            return c.title()
    return None

# ---------------- ANALYSE ----------------
def find_trade():
    markets = get_markets()
    best = None

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

        model = get_weather(city)
        edge = model - market

        if edge > EDGE_THRESHOLD:
            if not best or edge > best["edge"]:
                best = {
                    "city": city,
                    "model": model,
                    "market": market,
                    "edge": edge,
                    "title": m["question"]
                }

    return best

# ---------------- RESULT SIMULATION ----------------
def simulate_result():
    return random.choice(["WIN", "LOSS"])

# ---------------- MAIN ----------------
send("🚀 B4 TRACKING BOT gestartet")

while True:
    print("\n--- Neue Analyse ---")

    trade = find_trade()

    if trade:
        send(f"""
💰 TRADE
📍 {trade['city']}

📊 {trade['title']}

🧠 Model: {trade['model']:.1f}%
📊 Market: {trade['market']:.1f}%
📈 Edge: {trade['edge']:.1f}%

🎯 BUY YES
💵 ${STAKE}
""")

        result = simulate_result()

        if result == "WIN":
            data["balance"] += STAKE
            data["wins"] += 1
        else:
            data["balance"] -= STAKE
            data["losses"] += 1

        save_data(data)

        send(f"""
📊 RESULT: {result}
💰 Balance: {data['balance']}$
🏆 Wins: {data['wins']} ❌ Losses: {data['losses']}
""")

    else:
        print("❌ Kein Trade gefunden")

    time.sleep(120)
