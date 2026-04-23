import requests
import time
import re
from datetime import datetime

# =========================
# CONFIG
# =========================
TELEGRAM_TOKEN = "DEIN_TOKEN"
CHAT_ID = "DEINE_CHAT_ID"

# Nur aktive Märkte (Vienna entfernt)
CITIES = {
    "London": "https://polymarket.com/event/precipitation-in-london-in-april",
    "New York": "https://polymarket.com/event/precipitation-in-nyc-in-april",
    "Hong Kong": "https://polymarket.com/event/precipitation-in-hong-kong-in-april"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# =========================
# TELEGRAM
# =========================
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except Exception as e:
        print(f"Telegram Fehler: {e}")

# =========================
# WEATHER
# =========================
def get_weather(city):
    url = f"https://wttr.in/{city}?format=j1"
    data = requests.get(url).json()

    current = data["current_condition"][0]

    temp = float(current["temp_C"])
    wind = float(current["windspeedKmph"]) / 3.6  # m/s
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
# MARKET (robuster Scrape)
# =========================
def get_market_probability(url):
    try:
        html = requests.get(url, headers=HEADERS, timeout=10).text

        # Versuche mehrere Patterns (Seite ändert sich oft)
        patterns = [
            r'"lastPrice":\s*0\.(\d+)',   # 0.65 -> 65%
            r'(\d{1,2})\s?¢',            # 65¢
            r'(\d{1,2})\.\d%'            # 65.3%
        ]

        for p in patterns:
            match = re.search(p, html)
            if match:
                val = match.group(1)
                prob = float(val)
                if prob <= 1:  # falls 0.65 Format
                    prob = prob * 100
                return round(prob, 2)

        return None

    except Exception as e:
        print(f"Market Fehler: {e}")
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
    print("🚀 VALUE BOT (Real Data) läuft...")

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

                print(f"{city}: Model {model}% | Market {market}% | Edge {round(edge,2)}%")

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

        time.sleep(300)  # 5 Minuten

# =========================
# START
# =========================
if __name__ == "__main__":
    send_telegram("🧠 VALUE BOT ONLINE (Vienna entfernt, Profit Mode aktiv)")
    run_bot()
