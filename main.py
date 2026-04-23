import requests
import time
from datetime import datetime

# =========================
# CONFIG
# =========================
TELEGRAM_TOKEN = "DEIN_TOKEN"
CHAT_ID = "DEINE_CHAT_ID"

CITIES = {
    "Vienna": "https://polymarket.com/event/precipitation-in-vienna-in-april",
    "London": "https://polymarket.com/event/precipitation-in-london-in-april",
    "New York": "https://polymarket.com/event/precipitation-in-nyc-in-april",
    "Hong Kong": "https://polymarket.com/event/precipitation-in-hong-kong-in-april"
}

# =========================
# TELEGRAM
# =========================
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# =========================
# WEATHER
# =========================
def get_weather(city):
    url = f"https://wttr.in/{city}?format=j1"
    data = requests.get(url).json()

    current = data["current_condition"][0]

    temp = float(current["temp_C"])
    wind = float(current["windspeedKmph"]) / 3.6
    humidity = float(current["humidity"])
    clouds = float(current["cloudcover"])

    return temp, wind, humidity, clouds

# =========================
# MODEL
# =========================
def calculate_model_probability(temp, wind, humidity, clouds):
    score = 0

    if wind > 10:
        score += 3
    if humidity > 70:
        score += 3
    if clouds > 60:
        score += 2
    if temp < 15:
        score += 2

    return min(score * 10, 100)

# =========================
# MARKET REAL DATA (KEY PART)
# =========================
def get_market_probability(url):
    try:
        # einfacher Scrape der Seite (Fallback)
        html = requests.get(url).text

        # VERY BASIC extraction (stabil genug für jetzt)
        import re
        match = re.search(r'(\d{1,2}\.\d)%', html)

        if match:
            prob = float(match.group(1))
            return prob
        else:
            return None

    except:
        return None

# =========================
# VALUE FILTER
# =========================
def is_profitable(model, market):
    if market is None:
        return False, 0

    edge = model - market

    if edge > 10 and model >= 60 and market < 90:
        return True, edge

    return False, edge

# =========================
# MAIN LOOP
# =========================
def run_bot():
    print("🚀 VALUE BOT (REAL DATA) läuft...")

    while True:
        print("\n--- Neue Analyse Runde ---")

        for city, url in CITIES.items():
            try:
                temp, wind, humidity, clouds = get_weather(city)

                model = calculate_model_probability(temp, wind, humidity, clouds)
                market = get_market_probability(url)

                if market is None:
                    print(f"⚠️ Kein Market Data: {city}")
                    continue

                profitable, edge = is_profitable(model, market)

                print(f"{city}: Model {model}% | Market {market}% | Edge {edge}%")

                if profitable:
                    msg = f"""💰 VALUE TRADE 💰

📍 {city}
🌡️ {temp}°C
🌬️ Wind: {round(wind,2)} m/s
☁️ Clouds: {clouds}%
💧 Humidity: {humidity}%

🧠 Model: {model}%
📊 Market: {market}%
📈 Edge: +{round(edge,2)}%

🎯 ACTION: BUY YES

🔗 {url}

💸 Einsatz: max $2
"""

                    send_telegram(msg)

                else:
                    print(f"❌ Kein Value: {city}")

            except Exception as e:
                print(f"Fehler bei {city}: {e}")

        time.sleep(300)

# =========================
# START
# =========================
if __name__ == "__main__":
    send_telegram("🧠 VALUE BOT ONLINE (Real Market Data aktiv)")
    run_bot()
