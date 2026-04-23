import requests
import time
from datetime import datetime

# =========================
# CONFIG
# =========================
TELEGRAM_TOKEN = "DEIN_TOKEN"
CHAT_ID = "DEINE_CHAT_ID"

CITIES = ["Vienna", "London", "New York", "Hong Kong"]

# =========================
# TELEGRAM
# =========================
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# =========================
# WEATHER DATA
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
# MODEL (DEIN EDGE MODEL)
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

    return min(score * 10, 100)  # max 100%

# =========================
# MARKET (SIMULIERT – später ersetzen)
# =========================
def get_market_probability():
    import random
    return random.randint(40, 80)

# =========================
# VALUE FILTER
# =========================
def is_profitable(model, market):
    edge = model - market

    if edge > 10 and model >= 60 and market < 90:
        return True, edge
    return False, edge

# =========================
# MAIN LOOP
# =========================
def run_bot():
    print("🚀 VALUE BOT läuft...")

    while True:
        print("\n--- Neue Analyse Runde ---")

        for city in CITIES:
            try:
                temp, wind, humidity, clouds = get_weather(city)

                model = calculate_model_probability(temp, wind, humidity, clouds)
                market = get_market_probability()

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
📈 Edge: +{edge}%

🎯 ACTION: BUY YES

💸 Einsatz: max $2
"""

                    send_telegram(msg)

                else:
                    print(f"❌ Skip (kein Value): {city}")

            except Exception as e:
                print(f"Fehler bei {city}: {e}")

        time.sleep(300)  # alle 5 Minuten

# =========================
# START
# =========================
if __name__ == "__main__":
    send_telegram("✅ VALUE BOT ONLINE (Profit Mode aktiv)")
    run_bot()
